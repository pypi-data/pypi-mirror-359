import json
import os
import threading
import torch.distributed as dist

from torch.distributed.elastic.rendezvous import (RendezvousInfo,
                                                  RendezvousHandler,
                                                  RendezvousStoreInfo,
                                                  RendezvousParameters)
from ..logging import get_logger
from typing import Any, Dict, List, Optional, Tuple

logger = get_logger(__name__)


class HyperPodStore(dist.Store):
    """
    Using a HyperPodStore here to avoid overriding HyperPodElasticAgent._rendezvous.
    Most operations are no-ops as we are not using the store, instead the JobController
    sets the store_content using the /start API in the HyperPodRendezvousBackend.
    """

    def __init__(self, base_global_rank, global_world_size, base_role_rank,
                 role_world_size):
        super().__init__()
        self.store_content = [
            base_global_rank,
            global_world_size,
            base_role_rank,
            role_world_size,
        ]

    @classmethod
    def multi_get(cls, keys: List[str]) -> List[bytes]:
        return []

    @classmethod
    def multi_set(cls, keys: List[str], values: List[str]) -> None:
        return

    def get(self, key: str) -> bytes:
        return json.dumps(self.store_content).encode("utf-8")

    def set(self, key: str, value: str) -> None:
        return


class HyperpodRendezvousException(RuntimeError):
    """Raised when a Hyperpod rendezvous fails"""


class HyperPodRendezvousBackend(RendezvousHandler):

    def __init__(
        self,
        run_id: str,
        local_world_size: int,
        resource_config_dir: Optional[str] = None,
    ):
        self.run_id = run_id
        self.local_world_size = local_world_size
        self._lock = threading.Lock()
        self._group_rank: int = -1
        self._nnodes: int = -1
        self._master_addr: str = ""
        self._master_port: int = -1
        self._resource_config_dir = resource_config_dir or os.path.join(
            os.sep, "opt", "ml", "input", "config")
        self._resource_config_file = os.path.join(self._resource_config_dir,
                                                  "pod_resourceconfig.json")
        try:
            os.makedirs(self._resource_config_dir, exist_ok=True)
        except (PermissionError, OSError) as ex:
            raise HyperpodRendezvousException(ex)
        # Attempt to read resource config file if it already exists and
        # keep an in-memory copy of ip_version, so we don't have to fetch it from file for every `/status` call
        self.ip_version: Optional[str] = None
        if os.path.exists(self._resource_config_file):
            data = self._read_existing_resource_file()
            self.ip_version = data.get("ips_timestamp")

    def _read_existing_resource_file(self) -> Dict:
        try:
            with open(self._resource_config_file, "r") as f:
                return json.load(f)
        except OSError as ex:
            raise HyperpodRendezvousException(ex)

    def _save_file_atomic(self, data):
        temp_file_path = f"{self._resource_config_file}.tmp"
        with open(temp_file_path, "w") as f:
            json.dump(data, f)
        os.replace(temp_file_path, self._resource_config_file)

    def _update_resource_config(
        self,
        rank: int,
        ip_version: str,
        rank_ips: List[Dict[str, Any]],
    ):
        """
        Updates the pod_resourceconfig.json file with the rank_ips.
        The first call to this method contains `rank -> ip` mappings for all participating workers.
        Subsequent calls will ONLY contain `rank -> ip` mappings of workers which were re-ranked.
        NOTE: A mmap based implementation might be more optimal in the future given the update pattern for rank->ips.
        Field names are based on requirements specified here
        https://quip-amazon.com/MChlApG7eMCs/Compass-145k-Resilience-TCPStore-Removal-Support-passing-IP-Strings-data-Design#temp:C:cEN7c801b8e869845f5beb353819
        """
        if os.path.exists(self._resource_config_file):
            data = self._read_existing_resource_file()
            ips = data["ips"]
        else:
            data = {}
            ips = [None] * len(rank_ips)
        for item in rank_ips:
            try:
                ips[item["rank"]] = item["ip"]
            except (KeyError, IndexError) as ex:
                logger.error(
                    f"Failed to update {self._resource_config_file} with latest ranking info"
                )
                raise HyperpodRendezvousException(ex)
        data["ips"] = ips
        data["current_pod_ip"] = ips[rank]
        data["ips_timestamp"] = ip_version
        self._save_file_atomic(data)
        self.ip_version = data["ips_timestamp"]

    def set_rdzv_info(
        self,
        rank: int,
        nnodes: int,
        master_addr: str,
        master_port: int,
        ip_version: Optional[str],
        rank_ips: Optional[list],
    ) -> None:
        with self._lock:
            self._group_rank = rank
            self._nnodes = nnodes
            self._master_addr = master_addr
            self._master_port = master_port
            if ip_version is not None and rank_ips is not None:
                self._update_resource_config(rank, ip_version, rank_ips)

    def get_rdzv_info(self) -> Tuple[int, int, str, int]:
        """
        It is expected that the `set_rdzv_info` would be called before through the /start API to set the rdzv info

        WORLD_SIZE is calculated as `local_world_size * nnodes` and stays same for the lifecycle of the Agent/training.
        We don't support flexible nnodes e.g. `--nnodes=MIN_SIZE:MAX_SIZE` right now

        The RANK is the group_rank here.
        For instance, if we have `--nnodes=2 --nproc-per-node=2`. node=0 would get a RANK=0 and node=1 a RANK=1.
            The Agent would then assign local and global_ranks based on RANK (group_rank), nnodes and nproc-per-node
            Node=0, RANK=0, Worker=0 ===Agent assigns===> LOCAL_RANK=0, GLOBAL_RANK=0
            Node=0, RANK=0, Worker=1 ===Agent assigns===> LOCAL_RANK=1, GLOBAL_RANK=1
            Node=1, RANK=1, Worker=0 ===Agent assigns===> LOCAL_RANK=0, GLOBAL_RANK=2
            Node=1, RANK=1, Worker=1 ===Agent assigns===> LOCAL_RANK=1, GLOBAL_RANK=3
        In case we expect there to be agents with multiple roles on a cluster, the rendezvous logic would need changes
        and we'll need control plane to pass ROLE_RANK and ROLE_WORLD_SIZE as additional params through labels
        """
        with self._lock:
            return self._group_rank, self.local_world_size * self._nnodes, self._master_addr, self._master_port

    def get_backend(self) -> str:
        return "hyperpod"

    @property
    def use_agent_store(self) -> bool:
        return False

    def next_rendezvous(self) -> RendezvousInfo:
        """
        The Pod Reconciler writes a labels file with a RANK and WORLD_SIZE
        which is what is used for rendezvous instead of a backing distributed store here.
        We use `HyperPodStore` in order to avoid overriding methods in HyperPodElasticAgent.
        NOTE: Assuming that there was only 1 role used to launch all workers across the cluster.
              This would require controller to provide both through labels if role_rank != global_rank
        """
        group_rank, world_size, master_addr, master_port = self.get_rdzv_info()
        hyperpod_store = HyperPodStore(
            base_global_rank=group_rank * self.local_world_size,
            global_world_size=world_size,
            base_role_rank=group_rank * self.local_world_size,
            role_world_size=world_size,
        )
        return RendezvousInfo(
            store=hyperpod_store,
            rank=group_rank,
            world_size=world_size,
            bootstrap_store_info=RendezvousStoreInfo(master_addr, master_port),
        )

    def is_closed(self):
        return False

    def set_closed(self):
        pass

    def num_nodes_waiting(self):
        return 0

    def get_run_id(self) -> str:
        return self.run_id

    def shutdown(self) -> bool:
        return True


def create_rdzv_handler(params: RendezvousParameters) -> RendezvousHandler:
    return HyperPodRendezvousBackend(
        run_id=params.run_id,
        local_world_size=params.get("local_world_size", 1),
        resource_config_dir=params.get("resource_config_dir",
                                       None),  # For unit tests only
    )
