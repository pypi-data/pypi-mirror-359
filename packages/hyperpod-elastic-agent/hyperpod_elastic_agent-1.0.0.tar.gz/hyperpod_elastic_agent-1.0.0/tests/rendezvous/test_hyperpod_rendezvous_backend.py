import json
import os
import pytest
import shutil
import tempfile

from hyperpod_elastic_agent.rendezvous import (
    create_rdzv_handler,
    HyperPodRendezvousBackend,
    HyperpodRendezvousException,
)
from torch.distributed.elastic.rendezvous import RendezvousParameters

_run_id = "DEFAULT_RUN_ID"
ADDR = "192.168.111.1"
PORT = 23456
IP_VERSION = "2025-01-10T12:00:00Z"
RANK_IPS = [
    {
        "ip": "192.168.111.1",
        "rank": 0,
    },
    {
        "ip": "192.168.111.1",
        "rank": 1,
    },
    {
        "ip": "192.168.111.2",
        "rank": 2,
    },
    {
        "ip": "192.168.111.2",
        "rank": 3,
    },
]


class TestHyperpodRendezvousBackend:

    @classmethod
    def setup_class(cls):
        cls.resource_config_dir = tempfile.mkdtemp()
        rdzv_configs = dict(
            local_world_size=1,
            resource_config_dir=cls.resource_config_dir,
        )
        params = RendezvousParameters(
            backend="hyperpod",
            endpoint="",
            run_id=_run_id,
            min_nodes=1,
            max_nodes=1,
            **rdzv_configs,
        )
        cls.backend = create_rdzv_handler(params)
        assert isinstance(cls.backend, HyperPodRendezvousBackend)
        cls.backend.set_rdzv_info(
            rank=0,
            nnodes=1,
            master_addr=ADDR,
            master_port=PORT,
            ip_version=IP_VERSION,
            rank_ips=RANK_IPS,
        )

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.resource_config_dir, ignore_errors=True)

    def test_correct_value(self):
        rendezvous_info = self.backend.next_rendezvous()
        assert rendezvous_info.world_size == 1
        assert rendezvous_info.rank == 0
        assert rendezvous_info.bootstrap_store_info.master_addr == ADDR
        assert rendezvous_info.bootstrap_store_info.master_port == int(PORT)

    def test_backing_store(self):
        rendezvous_info = self.backend.next_rendezvous()
        store = rendezvous_info.store
        base_global_rank, global_world_size, _, _ = json.loads(
            store.get("dummy"))
        assert base_global_rank == 0
        assert global_world_size == 1

    def test_multi_proc(self):
        backend = HyperPodRendezvousBackend(
            run_id=_run_id,
            local_world_size=2,
            resource_config_dir=self.resource_config_dir,
        )
        backend.set_rdzv_info(
            rank=1,
            nnodes=2,
            master_addr=ADDR,
            master_port=PORT,
            ip_version=IP_VERSION,
            rank_ips=RANK_IPS,
        )
        rendezvous_info = backend.next_rendezvous()
        store = rendezvous_info.store
        base_global_rank, global_world_size, _, _ = json.loads(
            store.get("dummy"))
        assert base_global_rank == 2
        assert global_world_size == 4

    def test_overrides(self):
        assert self.backend.num_nodes_waiting() == 0
        assert self.backend.get_run_id() == _run_id
        assert self.backend.get_backend() == "hyperpod"
        assert not self.backend.use_agent_store
        self.backend.set_closed()
        assert self.backend.shutdown()
        assert not self.backend.is_closed()

    def test_store_dummy_ops(self):
        backend = HyperPodRendezvousBackend(
            run_id=_run_id,
            local_world_size=2,
            resource_config_dir=self.resource_config_dir,
        )
        backend.set_rdzv_info(
            rank=0,
            nnodes=2,
            master_addr=ADDR,
            master_port=PORT,
            ip_version=IP_VERSION,
            rank_ips=RANK_IPS,
        )
        rendezvous_info = backend.next_rendezvous()
        store = rendezvous_info.store
        store.set("dummy_key", "dummy_val")
        store.multi_set(["dummy_key1", "dummy_key2"],
                        ["dummy_val1", "dummy_val2"])
        resp_get = json.loads(store.get("dummy_key"))
        resp_multi_get = store.multi_get(["dummy_key1", "dummy_key2"])
        assert "dummy_key" not in resp_get
        assert b"dummy_key1" not in resp_multi_get
        assert b"dummy_key2" not in resp_multi_get

    def test_set_rdzv_info_success(self):
        with tempfile.TemporaryDirectory() as resource_config_dir:
            backend = HyperPodRendezvousBackend(
                run_id=_run_id,
                local_world_size=2,
                resource_config_dir=resource_config_dir,
            )
            # First call should create config file
            config_path = os.path.join(resource_config_dir,
                                       "pod_resourceconfig.json")
            assert not os.path.exists(config_path)
            # First call should add all participating ips to config file
            backend.set_rdzv_info(
                rank=0,
                nnodes=2,
                master_addr=ADDR,
                master_port=PORT,
                ip_version=IP_VERSION,
                rank_ips=RANK_IPS,
            )
            with open(config_path, "r") as f:
                data = json.load(f)
                assert data["ips_timestamp"] == IP_VERSION
                assert data["current_pod_ip"] == "192.168.111.1"
                ips = data["ips"]
                for item in RANK_IPS:
                    assert ips[item["rank"]] == item["ip"]
            # Send only two ips for update
            update_ips = [
                {
                    "ip": "192.168.111.2",
                    "rank": 0,
                },
                {
                    "ip": "192.168.111.1",
                    "rank": 2,
                },
            ]
            update_ip_version = "2025-01-12T12:00:00Z"
            backend.set_rdzv_info(
                rank=0,
                nnodes=2,
                master_addr=ADDR,
                master_port=PORT,
                ip_version=update_ip_version,
                rank_ips=update_ips,
            )
            with open(config_path, "r") as f:
                data = json.load(f)
                assert data["ips_timestamp"] == update_ip_version
                assert data["current_pod_ip"] == "192.168.111.2"
                ips = data["ips"]
                assert len(ips) == len(RANK_IPS)
                for item in update_ips:
                    assert ips[item["rank"]] == item["ip"]

    def test_set_rdzv_info_invalid_update_rank(self):
        assert isinstance(self.backend, HyperPodRendezvousBackend)
        update_ips = [
            {
                "ip": "192.168.111.1",
                "rank": 123456789,
            },
        ]
        update_ip_version = "2025-01-12T12:00:00Z"
        with pytest.raises(HyperpodRendezvousException) as err:
            self.backend.set_rdzv_info(
                rank=0,
                nnodes=1,
                master_addr=ADDR,
                master_port=PORT,
                ip_version=update_ip_version,
                rank_ips=update_ips,
            )
            assert "list assignment index out of range" in err.value

    def test_set_rdzv_info_empty_update(self):
        assert isinstance(self.backend, HyperPodRendezvousBackend)
        update_ip_version = "2025-01-12T12:00:00Z"
        self.backend.set_rdzv_info(
            rank=0,
            nnodes=1,
            master_addr=ADDR,
            master_port=PORT,
            ip_version=update_ip_version,
            rank_ips=[],
        )
        with open(
                os.path.join(self.resource_config_dir,
                             "pod_resourceconfig.json"), "r") as f:
            data = json.load(f)
            assert data["ips_timestamp"] == update_ip_version
            assert data["current_pod_ip"] == "192.168.111.1"
            ips = data["ips"]
            for item in RANK_IPS:
                assert ips[item["rank"]] == item["ip"]
