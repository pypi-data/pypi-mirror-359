import pytest
import signal

from hyperpod_elastic_agent.pcontext.pcontext import (
    HyperpodSubprocessContext,
    _validate_full_rank,
)
from concurrent.futures import ThreadPoolExecutor
from torch.distributed.elastic.multiprocessing.api import DefaultLogsSpecs
from torch.distributed.elastic.multiprocessing.subprocess_handler import SubprocessHandler
from unittest.mock import Mock, call, patch


class TestHyperpodSubprocessContext:

    @classmethod
    def setup_class(cls):
        # Mock dependencies and create a sample instance
        cls.name = "test_subprocess"
        cls.entrypoint = "/path/to/entrypoint"
        cls.args = {0: ("arg1", "arg2")}
        cls.envs = {0: {"ENV_VAR": "value"}}
        cls.logs_specs = DefaultLogsSpecs()
        cls.death_sig = signal.SIGTERM
        cls.signal_timeout = 10
        cls.log_line_prefixes = {0: "prefix"}

        # Create the instance to test
        cls.context = HyperpodSubprocessContext(
            name=cls.name,
            entrypoint=cls.entrypoint,
            args=cls.args,
            envs=cls.envs,
            logs_specs=cls.logs_specs,
            death_sig=cls.death_sig,
            signal_timeout=cls.signal_timeout,
            log_line_prefixes=cls.log_line_prefixes,
        )

    def test_init(self):
        """Test that the initialization sets the correct attributes"""
        assert self.context.name == self.name
        assert self.context.entrypoint == self.entrypoint
        assert self.context._death_sig == self.death_sig

    @patch('hyperpod_elastic_agent.pcontext.pcontext.wait')
    def test_close_single_method(self, mock_wait):
        mock_proc = Mock()
        # Process is still running
        mock_proc.poll.return_value = None
        mock_wait.return_value = (set(), set())
        mock_proc.pid = 1234

        mock_handler = Mock(spec=SubprocessHandler)
        mock_handler.proc = mock_proc

        # Call the method
        HyperpodSubprocessContext._close_single(
            mock_handler,
            signal.SIGTERM,
            self.signal_timeout,
        )

        # Verify method calls
        mock_handler.close.assert_has_calls(
            [call(death_sig=signal.SIGTERM),
             call(death_sig=signal.SIGKILL)])
        mock_proc.wait.assert_has_calls([call(self.signal_timeout), call()])

    @patch('hyperpod_elastic_agent.pcontext.pcontext.wait')
    def test_close_method(self, mock_wait):
        # Create mock subprocess handlers
        mock_handlers = {
            0: Mock(spec=SubprocessHandler),
            1: Mock(spec=SubprocessHandler)
        }
        self.context.subprocess_handlers = mock_handlers

        # Mock the executor and futures
        mock_future1 = Mock()
        mock_future2 = Mock()
        mock_executor_instance = Mock()
        mock_executor_instance.submit.side_effect = [
            mock_future1, mock_future2
        ]
        mock_wait.return_value = (set(), set())

        # Patch the ThreadPoolExecutor to return our mock
        with patch.object(
                ThreadPoolExecutor,
                '__enter__',
                return_value=mock_executor_instance,
        ) as mock_executor:
            self.context.close(timeout=30)

        assert mock_executor_instance.submit.call_count == 2
        mock_wait.assert_called_once()

    @patch('hyperpod_elastic_agent.pcontext.pcontext.wait')
    def test_close_method_process_exited(self, mock_wait):
        mock_handlers = {0: Mock(spec=SubprocessHandler)}
        self.context.subprocess_handlers = mock_handlers

        mock_proc = Mock()
        # Process is still running
        mock_proc.poll.return_value = 0
        mock_proc.pid = 1234
        mock_wait.return_value = (set(), set())

        mock_handler = Mock(spec=SubprocessHandler)
        mock_handler.proc = mock_proc

        mock_future = Mock()
        mock_executor_instance = Mock()
        mock_executor_instance.submit.side_effect = [mock_future]

        # Call the method
        with patch.object(
                ThreadPoolExecutor,
                '__enter__',
                return_value=mock_executor_instance,
        ) as mock_executor:
            self.context.close()

        # Verify method calls
        mock_handler.close.assert_not_called()
        mock_proc.wait.assert_not_called()

    def test_close_with_no_handlers(self):
        self.context.subprocess_handlers = {}
        self.context.close()

    def test_close_with_custom_death_signal(self):
        mock_handlers = {0: Mock(spec=SubprocessHandler)}
        self.context.subprocess_handlers = mock_handlers

        custom_sig = signal.SIGKILL
        with patch.object(self.context, '_close') as mock_close:
            self.context.close(death_sig=custom_sig)
            mock_close.assert_called_once_with(
                death_sig=custom_sig,
                timeout=self.signal_timeout,
            )

    def test_validate_full_rank(self):
        with pytest.raises(RuntimeError):
            _validate_full_rank({}, 10, "")
