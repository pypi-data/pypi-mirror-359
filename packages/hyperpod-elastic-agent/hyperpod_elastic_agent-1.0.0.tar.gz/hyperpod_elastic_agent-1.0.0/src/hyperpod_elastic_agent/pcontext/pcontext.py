import logging
import signal
import sys
import subprocess

from concurrent.futures import ThreadPoolExecutor, wait
from torch.distributed.elastic.multiprocessing import start_processes as og_start_process
from torch.distributed.elastic.multiprocessing.api import (
    LogsSpecs,
    PContext,
    SubprocessContext,
)
from torch.distributed.elastic.multiprocessing.subprocess_handler import SubprocessHandler
from typing import Any, Callable, Optional, Union
from ..logging import get_logger

logger = get_logger(__name__)


def _validate_full_rank(d: dict[int, Any], nprocs: int, what: str):
    actual_keys = set(d.keys())
    expected_keys = set(range(nprocs))

    if actual_keys != expected_keys:
        raise RuntimeError(
            f"{what}, local rank mapping mismatch,"
            f" expected: {expected_keys}, actual: {actual_keys}")


def _get_kill_signal() -> signal.Signals:
    """Get the kill signal. SIGKILL for unix, CTRL_C_EVENT for windows."""
    if sys.platform == "win32":
        return signal.CTRL_C_EVENT  # type: ignore[attr-defined] # noqa: F821
    else:
        return signal.SIGKILL


def start_processes(
    name: str,
    entrypoint: Union[Callable, str],
    args: dict[int, tuple],
    envs: dict[int, dict[str, str]],
    logs_specs: LogsSpecs,
    death_sig: signal.Signals,
    signal_timeout: int,
    log_line_prefixes: Optional[dict[int, str]] = None,
    start_method: str = "spawn",
) -> PContext:
    """
    Overrides torchelastic's SubprocessContext to customize it for HyperPod
    """
    if not isinstance(entrypoint, str):
        return og_start_process(
            name=name,
            entrypoint=entrypoint,
            args=args,
            envs=envs,
            logs_specs=logs_specs,
            log_line_prefixes=log_line_prefixes,
            start_method=start_method,
        )

    nprocs = len(args)
    _validate_full_rank(args, nprocs, "args")
    _validate_full_rank(envs, nprocs, "envs")

    context: PContext
    context = HyperpodSubprocessContext(
        name=name,
        entrypoint=entrypoint,
        args=args,
        envs=envs,
        logs_specs=logs_specs,
        death_sig=death_sig,
        signal_timeout=signal_timeout,
        log_line_prefixes=log_line_prefixes,
    )

    try:
        context.start()
        return context
    except Exception:
        context.close()
        raise


class HyperpodSubprocessContext(SubprocessContext):

    def __init__(
        self,
        name: str,
        entrypoint: str,
        args: dict[int, tuple],
        envs: dict[int, dict[str, str]],
        logs_specs: LogsSpecs,
        death_sig: signal.Signals,
        signal_timeout: int,
        log_line_prefixes: Optional[dict[int, str]] = None,
    ):
        super().__init__(
            name,
            entrypoint,
            args,
            envs,
            logs_specs,
            log_line_prefixes,
        )
        self._death_sig = death_sig
        self._signal_timeout = signal_timeout

    def close(self,
              death_sig: Optional[signal.Signals] = None,
              timeout: Optional[int] = None) -> None:
        if not death_sig:
            death_sig = self._death_sig
        if not timeout:
            timeout = self._signal_timeout
        super().close(death_sig, timeout)

    @staticmethod
    def _close_single(
        handler: SubprocessHandler,
        death_sig: signal.Signals,
        timeout: int = 30,
    ):
        if handler.proc.poll() is None:
            logger.warning(
                "Sending process %s closing signal %s",
                handler.proc.pid,
                death_sig.name,
            )
            handler.close(death_sig=death_sig)
        try:
            handler.proc.wait(timeout)
        except subprocess.TimeoutExpired:
            # Ignore the timeout expired exception, since
            # the child process will be forcefully terminated via SIGKILL
            pass
        if handler.proc.poll() is None:
            logger.warning(
                "Unable to shutdown process %s via %s, forcefully exiting via %s",
                handler.proc.pid,
                death_sig,
                _get_kill_signal(),
            )
            handler.close(death_sig=_get_kill_signal())
            handler.proc.wait()

    def _close(
        self,
        death_sig: signal.Signals,
        timeout: int = 30,
    ) -> None:
        if not self.subprocess_handlers:
            return
        with ThreadPoolExecutor() as executor:
            futures = []
            for handler in self.subprocess_handlers.values():
                futures.append(
                    executor.submit(
                        self._close_single,
                        handler,
                        death_sig,
                        timeout,
                    ))

            wait(futures)
