import os
import pytest
import time
import torch.distributed.elastic.rendezvous.registry as rdzv_registry

from hyperpod_elastic_agent.config import PrePostTrainConfig, ShutdownConfig
from hyperpod_elastic_agent.hyperpod_elastic_agent import HyperPodElasticAgent, start_api_server
from hyperpod_elastic_agent.run import register_hyperpod_rendezvous
from hyperpod_elastic_agent.server.server import AgentState
from dataclasses import dataclass
from torch.distributed.elastic.agent.server.api import RunResult, WorkerSpec, WorkerState, WorkerGroup
from torch.distributed.elastic.rendezvous import RendezvousParameters
from torch.distributed.elastic.multiprocessing import LogsSpecs, Std
from unittest.mock import Mock, patch
from typing import Tuple, Callable


def _echo(msg):
    return msg


@dataclass
class Conf:
    entrypoint: Callable
    local_world_size: int
    args: Tuple = ()
    role: str = "default"
    redirects: Std = Std.NONE
    tee: Std = Std.NONE


class TestHyperPodElasticAgent:

    @pytest.fixture
    def mock_logs_specs(self):
        mock = Mock(spec=LogsSpecs)
        mock._local_ranks_filter = None
        return mock

    @pytest.fixture
    def mock_server_specs(self):
        return {
            "host": "127.0.0.1",
            "port": 8000,
            "log_level": "info",
        }

    @pytest.fixture
    def mock_hyperpod_elastic_agent_server(self):
        with patch(
                'hyperpod_elastic_agent.hyperpod_elastic_agent.HyperPodElasticAgentServer'
        ) as mock:
            yield mock

    @pytest.fixture
    def mock_log_agent(self):
        with patch(
                'hyperpod_elastic_agent.hyperpod_elastic_agent.LogAgent'
        ) as mock:
            yield mock

    @pytest.fixture
    def mock_start_processes(self):
        with patch(
                'hyperpod_elastic_agent.hyperpod_elastic_agent.start_processes'
        ) as mock:
            yield mock

    @pytest.fixture
    @patch("tempfile.mkdtemp", return_value="/tmp/test_dir")
    def agent(self, mock_logs_specs, mock_server_specs,
              mock_hyperpod_elastic_agent_server, mock_log_agent):
        node_config = Conf(
            entrypoint=_echo,
            args=("foo", ),
            local_world_size=2,
        )
        additional_conf = {
            "local_world_size": 2,
            "resource_config_dir": "/tmp/test_dir",
        }
        rdzv_params = RendezvousParameters(
            backend="hyperpod",
            endpoint="",
            run_id="test_run",
            min_nodes=1,
            max_nodes=1,
            **additional_conf,
        )
        register_hyperpod_rendezvous()
        rdzv_handler = rdzv_registry.get_rendezvous_handler(rdzv_params)
        self.worker_spec = WorkerSpec(
            role=node_config.role,
            local_world_size=node_config.local_world_size,
            entrypoint=node_config.entrypoint,
            args=node_config.args,
            rdzv_handler=rdzv_handler,
            max_restarts=0,
            monitor_interval=0.01,
            master_addr=None,
            master_port=None,
        )
        pre_post_train_config = PrePostTrainConfig(
            pre_train_script="pre-train-script.sh",
            post_train_script="post-train-script.sh",
        )
        shutdown_config = ShutdownConfig(
            shutdown_timeout=15,
            shutdown_signal="SIGKILL",
        )
        version = "1.0.0"
        return HyperPodElasticAgent(self.worker_spec, mock_logs_specs,
                                    mock_server_specs, pre_post_train_config,
                                    shutdown_config, version)

    def test_init(self, agent, mock_hyperpod_elastic_agent_server,
                  mock_log_agent):
        assert agent._agent_state == AgentState.READY
        mock_hyperpod_elastic_agent_server.assert_called_once()
        mock_hyperpod_elastic_agent_server.return_value.start.assert_called_once(
        )

    def test_repr(self, agent):
        assert repr(agent).startswith("HyperPodElasticAgent(")

    def test_stop_workers(self, agent):
        worker_group = WorkerGroup(spec=self.worker_spec)
        agent._stop_workers(worker_group)
        assert worker_group.state == WorkerState.INIT
        assert agent._agent_state == AgentState.READY

    def test_initialize_workers(self, mock_start_processes, agent,
                                mock_log_agent):
        worker_group = agent.get_worker_group()
        agent._initialize_workers(worker_group)
        time.sleep(self.worker_spec.monitor_interval)
        mock_start_processes.assert_called_once()
        assert worker_group.state == WorkerState.HEALTHY
        mock_log_agent.assert_called_once()

    @patch(
        'hyperpod_elastic_agent.hyperpod_elastic_agent.LocalElasticAgent.run'
    )
    def test_run(self, mock_super_run, agent):
        agent.run()
        mock_super_run.assert_called_once()

    def test_set_agent_state(self, agent, mock_log_agent):
        agent.set_agent_state(AgentState.RUNNING)
        assert agent._agent_state == AgentState.RUNNING

    def test_get_agent_state_info(self, agent):
        agent.set_agent_state(AgentState.RUNNING)
        status, transitions, ip_version = agent.get_agent_state_info()
        assert status == AgentState.RUNNING
        assert all(state in transitions
                   for state in (AgentState.READY, AgentState.RUNNING))

    def test_get_run_result(self, agent):
        assert agent.get_run_result() == agent._run_result

    def test_shutdown(self, agent):
        agent._shutdown()
        assert agent._pcontext is None
        assert agent._agent_state == AgentState.READY

    def test_training_stages_generator(self, mock_start_processes,
                                       mock_log_agent, agent):
        stages = agent._training_stages_generator()
        agent.update_rendezvous_info(
            rank=0,
            nnodes=1,
            fault_count=23,
            master_addr="192.168.111.1",
            master_port=23456,
            ip_version="2025-01-10T12:00:00Z",
            rank_ips=[
                {
                    "ip": "192.168.111.1",
                    "rank": 0,
                },
            ],
        )

        # Pre-train stage
        next(stages)
        _, _, ip_version = agent.get_agent_state_info()
        assert agent._worker_group.state == WorkerState.HEALTHY
        assert ip_version == "2025-01-10T12:00:00Z"
        assert mock_start_processes.call_args.kwargs["name"] == "default"
        assert mock_start_processes.call_args.kwargs[
            "entrypoint"] == "pre-train-script.sh"
        mock_start_processes.reset_mock()

        # Training stage
        next(stages)
        assert agent._worker_group.state == WorkerState.HEALTHY
        assert mock_start_processes.call_args.kwargs["name"] == "default"
        assert mock_start_processes.call_args.kwargs["args"] == {
            0: ('foo', ),
            1: ('foo', )
        }
        assert mock_start_processes.call_args.kwargs["envs"][0][
            "TORCHELASTIC_RESTART_COUNT"] == "23"
        assert mock_start_processes.call_args.kwargs["envs"][0][
            "JOB_RESTART_COUNT"] == "23"
        assert mock_start_processes.call_args.kwargs["envs"][0][
            "MASTER_ADDR"] == "192.168.111.1"
        assert mock_start_processes.call_args.kwargs["envs"][0][
            "MASTER_PORT"] == "23456"
        assert mock_start_processes.call_args.kwargs["entrypoint"] == _echo

        # Post-train stage
        mock_start_processes.reset_mock()
        next(stages)
        assert agent._worker_group.state == WorkerState.HEALTHY
        assert mock_start_processes.call_args.kwargs["name"] == "default"
        assert mock_start_processes.call_args.kwargs[
            "entrypoint"] == "post-train-script.sh"

        # Generator should be exhausted
        with pytest.raises(StopIteration):
            next(stages)

        assert mock_log_agent.return_value.start.call_count == 3

    @patch('hyperpod_elastic_agent.hyperpod_elastic_agent.time.sleep')
    def test_invoke_run(self, mock_sleep, mock_start_processes, agent):
        agent._monitor_workers = Mock()
        agent._monitor_workers.side_effect = [
            RunResult(state=WorkerState.INIT),
            # Pre-train
            RunResult(state=WorkerState.SUCCEEDED),
            # Train
            RunResult(state=WorkerState.SUCCEEDED),
            # Post-train
            RunResult(state=WorkerState.SUCCEEDED),
        ]
        # Forcing out of _invoke_run loop through an exception
        mock_sleep.side_effect = [None, None, None, None, Exception("Forced")]

        agent.set_agent_state(AgentState.RUNNING)
        with pytest.raises(Exception, match="Forced"):
            agent._invoke_run()
        assert agent.get_agent_state_info()[0] == AgentState.COMPLETED
        assert mock_start_processes.call_count == 3

    @patch('hyperpod_elastic_agent.hyperpod_elastic_agent.time.sleep')
    def test_invoke_run_stage_failure(self, mock_sleep, mock_start_processes,
                                      agent):
        agent._monitor_workers = Mock()
        agent._monitor_workers.side_effect = [
            RunResult(state=WorkerState.INIT),
            # Pre-train
            RunResult(state=WorkerState.HEALTHY),
            RunResult(state=WorkerState.SUCCEEDED),
            # Train
            RunResult(state=WorkerState.UNKNOWN),
            RunResult(state=WorkerState.FAILED),
        ]
        # Forcing out of _invoke_run loop through an exception
        mock_sleep.side_effect = [
            None, None, None, None, None,
            Exception("Forced")
        ]

        agent.set_agent_state(AgentState.RUNNING)
        with pytest.raises(Exception, match="Forced"):
            agent._invoke_run()
        assert agent.get_agent_state_info()[0] == AgentState.FAULTED
        assert mock_start_processes.call_count == 2

    @patch.dict(os.environ, {"HYPERPOD_ELASTICAGENT_SERVER_MAX_RETRY": "3"})
    def test_start_api_server_launch_failure(
            self, mock_hyperpod_elastic_agent_server, mock_server_specs):
        mock_agent = Mock()
        mock_server = Mock()

        mock_hyperpod_elastic_agent_server.return_value = mock_server
        # Adding multiple side effects for the retry decorator
        mock_server.is_alive.side_effect = [False] * 6
        mock_server.started = False

        # Test when server is not alive
        with pytest.raises(
                ValueError,
                match="Exception in launching HyperPodElasticAgentServer"):
            start_api_server(mock_agent, {})

    @patch.dict(os.environ, {"HYPERPOD_ELASTICAGENT_SERVER_MAX_RETRY": "3"})
    @patch('hyperpod_elastic_agent.hyperpod_elastic_agent.time')
    def test_start_api_server_start_timeout(
            self, mock_time, mock_hyperpod_elastic_agent_server):
        mock_agent = Mock()
        mock_server = Mock()

        mock_hyperpod_elastic_agent_server.return_value = mock_server
        # Adding multiple side effects for the retry decorator
        mock_server.is_alive.side_effect = [True] * 9
        mock_server.started = False
        mock_time.time.side_effect = [0, 10] * 3
        mock_time.sleep = Mock()

        with pytest.raises(
                ValueError,
                match="Failed to launch HyperPodElasticAgentServer within"):
            start_api_server(mock_agent, {})

        mock_server.start.assert_called()
        mock_server.shutdown.assert_called()
