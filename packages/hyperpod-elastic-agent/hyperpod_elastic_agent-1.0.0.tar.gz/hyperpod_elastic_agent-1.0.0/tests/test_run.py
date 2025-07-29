import pytest
import shutil
import signal
import tempfile
import torch.distributed.elastic.rendezvous.registry as rdzv_registry
from argparse import ArgumentParser
from hyperpod_elastic_agent import HyperPodRendezvousBackend
from hyperpod_elastic_agent.run import (
    add_additional_hyperpod_args,
    additional_hyperpod_config_from_args,
    main,
    register_hyperpod_rendezvous,
)
from torch.distributed.elastic.agent.server import RunResult
from torch.distributed.elastic.agent.server.api import WorkerState
from torch.distributed.elastic.multiprocessing import ProcessFailure, SignalException
from torch.distributed.elastic.multiprocessing.errors import ChildFailedError
from torch.distributed.elastic.rendezvous import RendezvousParameters
from unittest.mock import Mock, patch


class TestRun:

    @classmethod
    def setup_class(cls):
        register_hyperpod_rendezvous()
        cls.custom_args = [
            "--pre-train-script",
            "pre_train.sh",
            "--pre-train-args",
            "'pre_1 pre_2 pre_3'",
            "--post-train-script",
            "post_train.sh",
            "--post-train-args",
            "'post_1 post_2 post_3'",
            "--server-port",
            "9090",
            "--server-log-level",
            "DEBUG",
            "--server-shutdown-timeout",
            "60",
            "--shutdown-signal",
            "SIGTERM",
            "--shutdown-timeout",
            "15",
        ]
        cls.resource_config_dir = tempfile.mkdtemp()
        cls.training_args = [
            "--rdzv-backend",
            "static",
            "--rdzv-conf",
            f"resource_config_dir='{cls.resource_config_dir}'",
            "unit_test_training.sh",
            "Training!!",
        ]

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.resource_config_dir)

    @pytest.fixture
    def mock_agent(self):
        with patch('hyperpod_elastic_agent.run.HyperPodElasticAgent'
                   ) as mock_agent:
            yield mock_agent

    def test_additional_hyperpod_config_from_args(self):
        parser = ArgumentParser()
        add_additional_hyperpod_args(parser)
        args = parser.parse_args(self.custom_args)
        pre_post_train_config, server_specs, shutdown_config = additional_hyperpod_config_from_args(
            args)
        assert pre_post_train_config.pre_train_script == "pre_train.sh"
        assert pre_post_train_config.pre_train_args == "'pre_1 pre_2 pre_3'"
        assert pre_post_train_config.post_train_script == "post_train.sh"
        assert pre_post_train_config.post_train_args == "'post_1 post_2 post_3'"
        assert shutdown_config.shutdown_timeout == 15
        assert shutdown_config.shutdown_signal == signal.SIGTERM
        assert server_specs["port"] == 9090
        assert server_specs["log_level"] == "DEBUG"
        assert server_specs["timeout_graceful_shutdown"] == 60
        assert server_specs["timeout_keep_alive"] == 5

    def test_register_hyperpod_rendezvous(self):
        rdzv_parameters = RendezvousParameters(
            backend="hyperpod",
            endpoint="dummy",
            min_nodes=1,
            max_nodes=1,
            run_id="TEST_ID",
            **dict(
                local_world_size=5,
                resource_config_dir=self.resource_config_dir,
            ),
        )
        handler = rdzv_registry.get_rendezvous_handler(rdzv_parameters)
        assert isinstance(handler, HyperPodRendezvousBackend)
        assert handler.get_backend() == "hyperpod"
        assert handler.get_run_id() == "TEST_ID"
        assert handler.local_world_size == 5

    def test_run_success(self, mock_agent):
        mock_agent_instance = mock_agent.return_value
        mock_agent_instance.run = Mock(return_value=RunResult(
            state=WorkerState.SUCCEEDED))
        main(self.custom_args + self.training_args)
        mock_agent.assert_called_once()
        mock_agent_instance.run.assert_called_once()

    def test_run_failure(self, mock_agent):
        mock_agent_instance = mock_agent.return_value
        run_result = RunResult(state=WorkerState.FAILED,
                               failures={
                                   0:
                                   ProcessFailure(local_rank=0,
                                                  pid=111,
                                                  exitcode=1,
                                                  error_file="dummy")
                               })
        mock_agent_instance.run = Mock(return_value=run_result)
        with pytest.raises(ChildFailedError) as cm:
            main(self.custom_args + self.training_args)
        assert cm.value.failures == run_result.failures

    def test_run_signal_exception(self, mock_agent):
        mock_agent_instance = mock_agent.return_value
        mock_agent_instance.run = Mock(side_effect=SignalException(
            msg="Dummy Exception",
            sigval=signal.SIGINT,
        ))
        with pytest.raises(Exception):
            main(self.custom_args + self.training_args)

    def test_unsupported_elasticity(self, mock_agent):
        with pytest.raises(AssertionError) as err:
            main(self.custom_args + ["--nnodes=1:4"] + self.training_args)
        assert str(
            err.value) == "Elastic cluster size is currently not supported"
