"""
HyperPod elastic agent
"""
import torch.distributed.elastic.rendezvous.registry as rdzv_registry
from argparse import ArgumentParser
from torch.distributed.run import config_from_args, get_args_parser
from torch.distributed.elastic import events, metrics
from torch.distributed.elastic.agent.server.api import WorkerSpec
from torch.distributed.elastic.multiprocessing import SignalException
from torch.distributed.elastic.multiprocessing.errors import ChildFailedError
from torch.distributed.elastic.rendezvous import RendezvousParameters
from torch.distributed.elastic.rendezvous.api import rendezvous_handler_registry as handler_registry
from torch.distributed.elastic.utils.logging import get_logger
from typing import Any, Dict, Tuple
from importlib.metadata import version

from .config import PrePostTrainConfig, ShutdownConfig
from .hyperpod_elastic_agent import HyperPodElasticAgent

logger = get_logger(__name__)
TIMEOUT_KEEP_ALIVE = 5


def run(args):
    config, cmd, cmd_args = config_from_args(args)
    version = _get_current_version()
    logger.info(f"Agent Version: {version}")
    pre_post_train_config, server_specs, shutdown_config = additional_hyperpod_config_from_args(
        args)
    if config.rdzv_backend != "hyperpod":
        logger.warning("Overriding `rdzv_backend='hyperpod'`")
        config.rdzv_backend = "hyperpod"

    # NOTE for future: When using elasticity (min_size!=max_size) DO NOT hard code assumptions about WORLD_SIZE
    #                  as the world size can change as nodes are allowed to leave and join.
    assert config.min_nodes == config.max_nodes, "Elastic cluster size is currently not supported"
    config.rdzv_configs["local_world_size"] = config.nproc_per_node
    rdzv_parameters = RendezvousParameters(
        backend=config.rdzv_backend,
        endpoint=config.rdzv_endpoint,
        run_id=config.run_id,
        min_nodes=config.min_nodes,
        max_nodes=config.max_nodes,
        local_addr=config.local_addr,
        **config.rdzv_configs,
    )

    # We don't use torch.dist.Store for the HyperPodElasticAgent, as such `master_addr` & `master_port` are set to None.
    # If it is required for the training job, it will be set through the /start API during rendezvous
    spec = WorkerSpec(
        role=config.role,
        local_world_size=config.nproc_per_node,
        entrypoint=cmd,
        args=tuple(cmd_args),
        rdzv_handler=rdzv_registry.get_rendezvous_handler(rdzv_parameters),
        monitor_interval=config.monitor_interval,
        master_addr=None,
        master_port=None,
        local_addr=config.local_addr,
    )
    agent = HyperPodElasticAgent(
        spec=spec,
        logs_specs=config.logs_specs,
        server_specs=server_specs,
        pre_post_train_config=pre_post_train_config,
        shutdown_config=shutdown_config,
        start_method=config.start_method,
        log_line_prefix_template=config.log_line_prefix_template,
        version=version,
    )

    try:
        metrics.initialize_metrics(metrics.MetricsConfig(config.metrics_cfg))

        result = agent.run()
        # records that agent.run() has succeeded NOT that workers have succeeded
        events.record(agent.get_event_succeeded())

        if result.is_failed():
            # ChildFailedError is treated specially by @record
            # if the error files for the failed children exist
            # @record will copy the first error (root cause)
            # to the error file of the launcher process.
            raise ChildFailedError(
                name=cmd,
                failures=result.failures,
            )

        return result.return_values
    except ChildFailedError:
        raise
    except SignalException:
        events.record(agent.get_event_failed())
        raise
    except Exception:
        events.record(agent.get_event_failed())
        raise
    finally:
        agent.shutdown_server()


def _get_current_version() -> str:
    return version("hyperpod_elastic_agent")


def _create_hyperpod_rendezvous_handler(params: RendezvousParameters):
    from hyperpod_elastic_agent.rendezvous.hyperpod_rendezvous_backend import create_rdzv_handler
    return create_rdzv_handler(params)


def register_hyperpod_rendezvous():
    handler_registry.register("hyperpod", _create_hyperpod_rendezvous_handler)


def add_additional_hyperpod_args(parser: ArgumentParser):
    """
    Adds ``pre-train`` and ``post-train`` related ``args``.
    .. note:: --pre-train-args and --post-train-args are opaque strings that are passed
              as is to the pre/post train scripts
              e.g. hyperpodrun --nnodes 1 \
                               --pre-train-script pre.sh --pre-train-args "arg1 arg2 ..." \
                               --post-train-script post.sh --post-train-args "arg1 arg2 ..." \
                               train arg1 arg2 ...
    :param parser: argument parser from torchrun
    :return:
    """
    parser.add_argument(
        "--shutdown-signal",
        default="SIGKILL",
        choices=["SIGTERM", "SIGKILL"],
        type=str,
        help="Signal to send to workers to shutdown. Default is SIGKILL. "
        "If SIGTERM, the Agent will wait `--shutdown-timeout` secs for process to finish gracefully "
        "before sending a SIGKILL.",
    )
    parser.add_argument(
        "--shutdown-timeout",
        default=30,
        type=int,
        help=
        "Worker shutdown timeout (in seconds) between SIGTERM and SIGKILL signals."
    )
    pretrain = parser.add_argument_group('pretrain')
    pretrain.add_argument(
        "--pre-train-script",
        type=str,
        help=
        "Full path to the (single GPU) pre training program/script to be launched, "
        "This is run on every restart of the training script. "
        "NOTE: Only 1 process is run per worker group",
    )
    pretrain.add_argument(
        "--pre-train-args",
        type=str,
        help="Opaque string that is passed as is to the pre train script")
    posttrain = parser.add_argument_group('posttrain')
    posttrain.add_argument(
        "--post-train-script",
        type=str,
        help=
        "Full path to the (single GPU) pre training program/script to be launched, "
        "This is run on every restart of the training script. "
        "NOTE: Only 1 process is run per worker group",
    )
    posttrain.add_argument(
        "--post-train-args",
        type=str,
        help="Opaque string that is passed as is to the post train script")
    server = parser.add_argument_group('server')
    server.add_argument(
        "--server-host",
        default="0.0.0.0",
        type=str,
        help="Agent server address",
    )
    server.add_argument(
        "--server-port",
        default=8080,
        type=int,
        help="Agent server port",
    )
    server.add_argument(
        "--server-log-level",
        default="info",
        type=str,
        help="Agent server log level",
    )
    server.add_argument("--server-shutdown-timeout",
                        type=int,
                        default=300,
                        help="Server shutdown timeout in seconds")


def additional_hyperpod_config_from_args(
        args) -> Tuple[PrePostTrainConfig, Dict[str, Any], ShutdownConfig]:
    pre_post_config = PrePostTrainConfig(
        pre_train_script=args.pre_train_script,
        post_train_script=args.post_train_script,
        pre_train_args=args.pre_train_args,
        post_train_args=args.post_train_args,
    )
    server_specs = dict(
        host=args.server_host,
        port=args.server_port,
        log_level=args.server_log_level,
        timeout_graceful_shutdown=args.server_shutdown_timeout,
        timeout_keep_alive=TIMEOUT_KEEP_ALIVE,
    )
    shutdown_config = ShutdownConfig(
        shutdown_timeout=args.shutdown_timeout,
        shutdown_signal=args.shutdown_signal,
    )
    return pre_post_config, server_specs, shutdown_config


def main(args=None):
    register_hyperpod_rendezvous()
    parser = get_args_parser()
    add_additional_hyperpod_args(parser)
    args = parser.parse_args(args)
    run(args)


if __name__ == "__main__":
    main()
