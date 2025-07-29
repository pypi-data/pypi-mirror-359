import os
import signal
import tempfile
import threading
import time

from .config import PrePostTrainConfig, ShutdownConfig
from .rendezvous import HyperPodRendezvousBackend
from .server import AgentState, HyperPodElasticAgentServer, VALID_TRANSITIONS
from .logagent.log_agent import LogAgent, LogState
from .logging import get_logger
from .pcontext import start_processes
from .util import retry
from datetime import datetime, timezone
from string import Template
from torch.distributed.elastic.agent.server.api import (
    RunResult,
    Worker,
    WorkerGroup,
    WorkerSpec,
    WorkerState,
    DEFAULT_ROLE,
)
from torch.distributed.elastic.agent.server.local_elastic_agent import LocalElasticAgent
from torch.distributed.elastic.metrics import put_metric
from torch.distributed.elastic.metrics.api import prof
from torch.distributed.elastic.multiprocessing import LogsSpecs
from torch.distributed.elastic.utils import macros
from typing import Any, Dict, List, Optional, Tuple, Union

logger = get_logger(__name__)
agent_state_lock = threading.Lock()

# TODO(mohaan): move these to server args
agent_server_max_retry = int(
    os.environ.get("HYPERPOD_ELASTICAGENT_SERVER_MAX_RETRY", "3"))
agent_server_delay = float(
    os.environ.get("HYPERPOD_ELASTICAGENT_SERVER_DELAY", "1"))
agent_server_timeout = float(
    os.environ.get("HYPERPOD_ELASTICAGENT_SERVER_TIMEOUT", "5"))


@retry(
    (ValueError, ),
    max_retries=agent_server_max_retry,
    delay=agent_server_delay,
)
def start_api_server(
    agent,
    server_specs,
    interval=0.5,
):
    server = HyperPodElasticAgentServer(agent, server_specs)
    server.start()
    expiry = time.time() + agent_server_timeout
    while server.is_alive() and not server.started and time.time() < expiry:
        time.sleep(interval)
    # Server startup failed and server thread exited
    if not server.is_alive():
        raise ValueError("Exception in launching HyperPodElasticAgentServer")
    # Server didn't start within the stipulated timeout
    if server.is_alive() and not server.started:
        server.shutdown()
        server.join()
        raise ValueError(
            f"Failed to launch HyperPodElasticAgentServer within {agent_server_timeout}s"
        )
    return server


class HyperPodElasticAgent(LocalElasticAgent):

    def __init__(
        self,
        spec: WorkerSpec,
        logs_specs: LogsSpecs,
        server_specs: dict,
        pre_post_train_config: PrePostTrainConfig,
        shutdown_config: ShutdownConfig,
        version: str,
        start_method="spawn",
        exit_barrier_timeout: float = 300,
        log_line_prefix_template: Optional[str] = None,
    ):
        super().__init__(
            spec,
            logs_specs,
            start_method,
            exit_barrier_timeout,
            log_line_prefix_template,
        )
        self._pre_post_train_config = pre_post_train_config
        self._shutdown_config = shutdown_config
        self._run_result = RunResult(state=self._worker_group.state)
        self._training_stages_gen = self._training_stages_generator()
        self._server_thread = start_api_server(self, server_specs)
        self._agent_state = AgentState.READY
        self._log_monitoring_configuration: Union[Dict[str, str], None] = None
        self._log_agent = LogAgent(spec.local_world_size)
        self._pre_train_wg, self._train_wg, self._post_train_wg = None, self._worker_group, None
        self.train_log_dir, self.pre_train_log_dir, self.post_train_log_dir = os.devnull, os.devnull, os.devnull
        if self._logs_specs.root_log_dir != os.devnull:
            self.train_log_dir = tempfile.mkdtemp(
                prefix=f"{spec.rdzv_handler.get_run_id()}_",
                dir=self._logs_specs.root_log_dir,
            )
        if isinstance(self._pre_post_train_config.pre_train_script, str):
            if self._logs_specs.root_log_dir != os.devnull:
                self.pre_train_log_dir = tempfile.mkdtemp(
                    prefix=f"pre_train_{spec.rdzv_handler.get_run_id()}_",
                    dir=self._logs_specs.root_log_dir,
                )
            pre_train_spec = WorkerSpec(
                role=spec.role,
                local_world_size=1,
                entrypoint=self._pre_post_train_config.pre_train_script,
                args=tuple([self._pre_post_train_config.pre_train_args]),
                rdzv_handler=spec.rdzv_handler,
                monitor_interval=spec.monitor_interval,
                master_addr=spec.master_addr,
                master_port=spec.master_port,
                local_addr=spec.local_addr,
            )
            self._pre_train_wg = WorkerGroup(pre_train_spec)
        if isinstance(self._pre_post_train_config.post_train_script, str):
            if self._logs_specs.root_log_dir != os.devnull:
                self.post_train_log_dir = tempfile.mkdtemp(
                    prefix=f"post_train_{spec.rdzv_handler.get_run_id()}_",
                    dir=self._logs_specs.root_log_dir,
                )
            post_train_spec = WorkerSpec(
                role=spec.role,
                local_world_size=1,
                entrypoint=self._pre_post_train_config.post_train_script,
                args=tuple([self._pre_post_train_config.post_train_args]),
                rdzv_handler=spec.rdzv_handler,
                monitor_interval=spec.monitor_interval,
                master_addr=spec.master_addr,
                master_port=spec.master_port,
                local_addr=spec.local_addr,
            )
            self._post_train_wg = WorkerGroup(post_train_spec)
        self._agent_transitions = {
            self._agent_state: datetime.now(timezone.utc).isoformat()
        }
        self.version = version

    def __repr__(self):
        return f"HyperPodElasticAgent({self._worker_group.spec!r})"

    def _stop_workers(self,
                      worker_group: WorkerGroup,
                      is_restart: bool = False) -> None:
        logger.info("Stopping workers...")
        self._shutdown(death_sig=self._shutdown_config.shutdown_signal,
                       is_restart=is_restart)
        self._log_agent.stop(clear_log_monitoring_configuration=True)
        worker_group.state = WorkerState.INIT
        self.set_agent_state(AgentState.READY)
        # Reset the generator
        self._training_stages_gen = self._training_stages_generator()

    def _training_stages_generator(self):
        if self._pre_train_wg:
            setattr(self._logs_specs, "_run_log_dir", self.pre_train_log_dir)
            self._worker_group = self._pre_train_wg
            super()._initialize_workers(self._worker_group)
            attempt_dir = LogAgent.compute_attempt_dir(
                run_log_dir=getattr(self._logs_specs, "_run_log_dir", ""),
                attempt_num=self._worker_group.spec.max_restarts -
                self._remaining_restarts)
            # Start log monitoring only for local rank 0 since local world size for pre train script is 1
            self._log_agent.start(attempt_dir, {0},
                                  self._log_monitoring_configuration)
        else:
            logger.debug(
                f"Skipping pre_train as script is either not specified "
                f"or not a string type: {self._pre_post_train_config.pre_train_script}"
            )
            self._worker_group.state = WorkerState.SUCCEEDED
        yield

        setattr(self._logs_specs, "_run_log_dir", self.train_log_dir)
        self._worker_group = self._train_wg
        super()._initialize_workers(self._worker_group)
        attempt_dir = LogAgent.compute_attempt_dir(
            run_log_dir=getattr(self._logs_specs, "_run_log_dir", ""),
            attempt_num=self._worker_group.spec.max_restarts -
            self._remaining_restarts)
        # Start log monitoring only for local rank 0 by default
        self._log_agent.start(attempt_dir, {0},
                              self._log_monitoring_configuration)
        yield

        if self._post_train_wg:
            setattr(self._logs_specs, "_run_log_dir", self.post_train_log_dir)
            self._worker_group = self._post_train_wg
            super()._initialize_workers(self._worker_group)
            attempt_dir = LogAgent.compute_attempt_dir(
                run_log_dir=getattr(self._logs_specs, "_run_log_dir", ""),
                attempt_num=self._worker_group.spec.max_restarts -
                self._remaining_restarts)
            # Start log monitoring only for local rank 0 since local world size for post train script is 1
            self._log_agent.start(attempt_dir, {0},
                                  self._log_monitoring_configuration)
        else:
            logger.debug(
                f"Skipping post_train as script is either not specified "
                f"or not a string: {self._pre_post_train_config.post_train_script}"
            )
            self._worker_group.state = WorkerState.SUCCEEDED
        yield

        self._log_agent.stop(clear_log_monitoring_configuration=True)

    @prof
    def _start_workers(self, worker_group: WorkerGroup) -> Dict[int, Any]:
        """
        Overriding just to add a single new env variable
        """
        logger.info(
            f"Starting workers with worker spec {worker_group.spec=}...")
        assert not worker_group.spec.rdzv_handler.use_agent_store, "HyperPod Agent store cannot be re-used for training"
        spec = worker_group.spec
        store = worker_group.store
        assert store is not None
        restart_count = spec.max_restarts - self._remaining_restarts

        use_agent_store: bool = spec.rdzv_handler.use_agent_store

        args: Dict[int, Tuple] = {}
        envs: Dict[int, Dict[str, str]] = {}
        log_line_prefixes: Optional[Dict[
            int, str]] = {} if self._log_line_prefix_template else None
        for worker in worker_group.workers:
            local_rank = worker.local_rank
            worker_env = {
                "LOCAL_RANK":
                str(local_rank),
                "RANK":
                str(worker.global_rank),
                "GROUP_RANK":
                str(worker_group.group_rank),
                "ROLE_RANK":
                str(worker.role_rank),
                "ROLE_NAME":
                spec.role,
                "LOCAL_WORLD_SIZE":
                str(spec.local_world_size),
                "WORLD_SIZE":
                str(worker.world_size),
                "GROUP_WORLD_SIZE":
                str(worker_group.group_world_size),
                "ROLE_WORLD_SIZE":
                str(worker.role_world_size),
                "MASTER_ADDR":
                worker_group.master_addr,
                "MASTER_PORT":
                str(worker_group.master_port),
                "JOB_RESTART_COUNT":
                str(restart_count),
                "TORCHELASTIC_RESTART_COUNT":
                str(restart_count),
                "TORCHELASTIC_MAX_RESTARTS":
                str(spec.max_restarts),
                "TORCHELASTIC_RUN_ID":
                spec.rdzv_handler.get_run_id(),
                "TORCHELASTIC_USE_AGENT_STORE":
                str(use_agent_store),
                "TORCH_NCCL_ASYNC_ERROR_HANDLING":
                os.getenv("TORCH_NCCL_ASYNC_ERROR_HANDLING", str(1)),
            }
            if "OMP_NUM_THREADS" in os.environ:
                worker_env["OMP_NUM_THREADS"] = os.environ["OMP_NUM_THREADS"]

            # export TORCHELASTIC_LOG_LINE_PREFIX_TEMPLATE="[rank\$rank-group_rank\$group_rank-attempt\$restart_count]:"
            if self._log_line_prefix_template:
                log_line_prefix = Template(
                    self._log_line_prefix_template).safe_substitute(
                        role_name=spec.role,
                        rank=worker.global_rank,
                        local_rank=local_rank,
                        group_rank=worker_group.group_rank,
                        restart_count=restart_count,
                    )
                log_line_prefixes[local_rank] = log_line_prefix

            envs[local_rank] = worker_env
            worker_args = list(spec.args)
            worker_args = macros.substitute(worker_args, str(local_rank))
            args[local_rank] = tuple(worker_args)

        self._setup_local_watchdog(envs=envs)
        self._setup_healthcheck()

        assert spec.entrypoint is not None
        assert self._logs_specs is not None
        self._pcontext = start_processes(
            name=spec.role,
            entrypoint=spec.entrypoint,
            args=args,
            envs=envs,
            logs_specs=self._logs_specs,
            death_sig=self._shutdown_config.shutdown_signal,
            signal_timeout=self._shutdown_config.shutdown_timeout,
            log_line_prefixes=log_line_prefixes,
            start_method=self._start_method,
        )

        return self._pcontext.pids()

    def _shutdown(self,
                  death_sig: signal.Signals = signal.SIGTERM,
                  is_restart: bool = False) -> None:
        logger.info(f"Shutting down workers with signal {death_sig}...")
        if self._worker_watchdog is not None:
            self._worker_watchdog.stop()
            self._worker_watchdog = None
        if self._health_check_server is not None:
            self._health_check_server.stop()
            self._health_check_server = None
        if self._pcontext:
            self._pcontext.close(
                death_sig=death_sig,
                timeout=self._shutdown_config.shutdown_timeout,
            )
            self._pcontext = None
        if not is_restart and self._rdzv_handler:
            self._rdzv_handler.shutdown()
        self._log_agent.stop(clear_log_monitoring_configuration=True)

    def _monitor_workers(self, worker_group: WorkerGroup) -> RunResult:
        logger.debug("Checking worker status...")
        # self._pcontext is None if
        # 1. Workers have not been started yet, or
        # 2. Workers were stopped
        if self._pcontext is None:
            return RunResult(state=worker_group.state)
        run_result = super()._monitor_workers(worker_group)
        # Additionally, check LogAgent state
        for log_eval_result in self._log_agent.log_eval_results:
            if log_eval_result.log_state in {LogState.SLOW, LogState.HANGING}:
                run_result.state = WorkerState.UNHEALTHY
                break
        return run_result

    def _get_worker_state(self, worker: Worker, result: RunResult) -> str:
        failure = result.failures.get(worker.global_rank)
        if not failure and result.state in {
                WorkerState.UNHEALTHY, WorkerState.FAILED
        }:
            # The worker got terminated by the torchelastic agent via SIGTERM signal
            return "TERMINATED"
        elif failure or worker.global_rank in result.return_values:
            return result.state.value
        elif self._agent_state == AgentState.SHUTDOWN:
            # For a graceful shutdown of the agent
            return "SHUTDOWN"
        else:
            raise ValueError(f"Unknown worker: {worker.global_rank}")

    def set_agent_state(self, agent_state: AgentState) -> None:
        with agent_state_lock:
            if agent_state in VALID_TRANSITIONS[self._agent_state]:
                logger.info(
                    f"Transitioning from {self._agent_state} to {agent_state}")
                self._agent_state = agent_state
                self._agent_transitions[agent_state] = datetime.now(
                    timezone.utc).isoformat()
            else:
                logger.error(
                    f"Invalid agent state transition from {self._agent_state} to {agent_state}."
                )

    def get_agent_state_info(
            self) -> Tuple[AgentState, Dict[AgentState, str], Optional[str]]:
        assert isinstance(self._rdzv_handler, HyperPodRendezvousBackend)
        return self._agent_state, self._agent_transitions, self._rdzv_handler.ip_version

    def update_rendezvous_info(
        self,
        rank: int,
        nnodes: int,
        fault_count: int,
        master_addr: str,
        master_port: int,
        ip_version: str,
        rank_ips: List[Dict[str, Any]],
    ):
        spec = self._worker_group.spec
        if isinstance(spec.rdzv_handler, HyperPodRendezvousBackend):
            spec.rdzv_handler.set_rdzv_info(rank, nnodes, master_addr,
                                            master_port, ip_version, rank_ips)
        else:
            raise RuntimeError(
                f"Unexpected rendezvous backend: {type(spec.rdzv_handler)}")
        # The API assigns `restart_count = spec.max_restarts - self._remaining_restarts`
        # updating `self._remaining_restarts` to avoid overriding torch.distributed.elastic.server.api._rendezvous
        # Currently `_remaining_restarts` is not being used anywhere else in torchelastic
        # except to calculate the `restart_count`
        self._remaining_restarts = spec.max_restarts - fault_count
        logger.update_run_info(rank, fault_count)

    def get_run_result(self) -> RunResult:
        return self._run_result

    def set_log_monitoring_configuration(self, config: Union[Dict[str, str],
                                                             None]):
        self._log_monitoring_configuration = config

    def get_log_agent_state(self) -> Tuple[LogState, Optional[List[str]]]:
        """
        Returns a common LogState and offending rule names based on the LogAgent state across
        all the local_ranks, similar to WorkerState.
        This is used for setting the `reason` and `message` field of the StatusResponse
        """
        for log_eval_result in self._log_agent.log_eval_results:
            if log_eval_result.log_state == LogState.HANGING:
                logger.info(
                    f"LogState.HANGING for rules={log_eval_result.rule_names}")
                return LogState.HANGING, log_eval_result.rule_names
            if log_eval_result.log_state == LogState.SLOW:
                logger.info(
                    f"LogState.SLOW for rules={log_eval_result.rule_names}")
                return LogState.SLOW, log_eval_result.rule_names
        if LogState.WAITING in self._log_agent.log_state:
            return LogState.WAITING, None
        return LogState.HEALTHY, None

    def shutdown_server(self) -> None:
        self._server_thread.shutdown()
        self._server_thread.join()

    def _invoke_run(self, role: str = DEFAULT_ROLE) -> RunResult:
        """
        There are a few changes from LocalElasticAgent to HyperPodElasticAgent:
        * The agent state transitions now depend both on the worker state
          and the Job Controller making API calls to the associated `self._server_thread`
        * We don't immediately start the workers, but wait in WorkerState.INIT state
          until we get a /start call from the controller, which updates the rdzv info
          before updating the AgentState
        * We don't shut down the agent on worker success, but wait for either an explicit
          /shutdown call or the controller to remove the pod that the agent is running inside
        """
        spec = self._worker_group.spec
        role = spec.role
        monitor_interval = spec.monitor_interval

        while self._agent_state != AgentState.SHUTDOWN:
            time.sleep(monitor_interval)
            self._run_result = self._monitor_workers(self._worker_group)
            state = self._run_result.state
            self._worker_group.state = state

            put_metric(f"workers.{role}.{state.name.lower()}", 1)
            # TODO(mohaan): Encapsulate this into a FSM for better readability
            if state == WorkerState.INIT:
                logger.debug(f"[{role}] worker group ready to start.")
                if self._agent_state == AgentState.RUNNING:
                    logger.info(
                        f"[{role}] Agent starting workers for entrypoint: {spec.get_entrypoint_name()}."
                    )
                    next(self._training_stages_gen)
                elif self._agent_state == AgentState.STOPPING:
                    self._stop_workers(self._worker_group)
            elif state == WorkerState.SUCCEEDED:
                if self._agent_state == AgentState.RUNNING:
                    try:
                        next(self._training_stages_gen)
                    except StopIteration:
                        logger.info(
                            f"[{role}] worker group successfully finished.")
                        self.set_agent_state(AgentState.COMPLETED)
                elif self._agent_state == AgentState.STOPPING:
                    self._stop_workers(self._worker_group)
            elif state in {WorkerState.UNHEALTHY, WorkerState.FAILED}:
                self._worker_group.state = WorkerState.FAILED
                if self._agent_state == AgentState.RUNNING:
                    logger.error(
                        f"[{role}] worker group changed to {state} state.")
                    self.set_agent_state(AgentState.FAULTED)
                elif self._agent_state == AgentState.STOPPING:
                    self._stop_workers(self._worker_group)
            elif state == WorkerState.HEALTHY:
                # No need to handle membership changes
                logger.debug(f"[{role}] worker group running.")
                if self._agent_state == AgentState.STOPPING:
                    self._stop_workers(self._worker_group)
            else:
                logger.error(
                    f"[{role}] Worker group in unrecoverable {state.name} state"
                )
        logger.info(f"[{role}] Shutting down agent...")
        self.shutdown_server()
        return self._run_result
