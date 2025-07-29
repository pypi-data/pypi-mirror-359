import json
import threading
import uvicorn

from .util import AgentState, StatusResponse, StatusResponseJSONEncoder
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from http import HTTPStatus
from torch.distributed.elastic.utils.logging import get_logger

logger = get_logger(__name__)


class HyperPodElasticAgentServer(threading.Thread):
    """
    Starts a new thread running a FastAPI+uvicorn based server to receive commands from Job Controller
    and updates the state machine for the JobAgent.
    The `status` API reads the `RunResult` state of the workers and returns it as a JSON response.
    """

    def __init__(self, agent, server_specs):
        super().__init__()
        self._app = FastAPI()
        self._register_routes()
        self._agent = agent
        config = uvicorn.Config(self._app, **server_specs)
        self._server = uvicorn.Server(config)

    @property
    def started(self):
        return self._server.started

    def _register_routes(self):
        self._app.add_api_route("/start", self._api_start, methods=["POST"])
        self._app.add_api_route("/stop", self._api_stop, methods=["POST"])
        self._app.add_api_route("/status", self._api_status, methods=["GET"])
        self._app.add_api_route("/shutdown",
                                self._api_shutdown,
                                methods=["POST"])

    async def _api_start(self, request: Request) -> Response:
        request_dict = await request.json()
        try:
            rank = int(request_dict.pop("rank"))
            nnodes = int(request_dict.pop("nnodes"))
            fault_count = int(request_dict.pop("faultCount"))
            master_addr = request_dict.pop("master_addr")
            master_port = int(request_dict.pop("master_port"))
            log_monitoring_configuration = request_dict.get(
                "log_monitoring_configuration")
            ip_version = request_dict.pop("ipVersion", None)
            rank_ips = request_dict.pop("rankIps", None)
            self._agent.update_rendezvous_info(rank, nnodes, fault_count,
                                               master_addr, master_port,
                                               ip_version, rank_ips)
            self._agent.set_log_monitoring_configuration(
                log_monitoring_configuration)
            self._agent.set_agent_state(AgentState.RUNNING)
            return Response(status_code=HTTPStatus.OK)
        except (KeyError, ValueError) as exc:
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST,
                                content=str(exc))

    def _api_stop(self) -> Response:
        self._agent.set_agent_state(AgentState.STOPPING)
        return Response(status_code=HTTPStatus.OK)

    def _api_status(self) -> Response:
        run_result = self._agent.get_run_result()
        log_state, log_rule_names = self._agent.get_log_agent_state()
        status, transitions, ip_version = self._agent.get_agent_state_info()
        agent_version = self._agent.version
        status_resp = StatusResponse(
            status=status,
            log_state=log_state,
            run_result=run_result,
            transitions=transitions,
            agent_version=agent_version,
            ip_version=ip_version,
            log_rule_names=log_rule_names,
        )
        resp_txt = json.dumps(status_resp,
                              ensure_ascii=False,
                              allow_nan=False,
                              indent=None,
                              separators=(",", ":"),
                              cls=StatusResponseJSONEncoder).encode("utf-8")
        return Response(resp_txt)

    def _api_shutdown(self) -> Response:
        self._agent.set_agent_state(AgentState.SHUTDOWN)
        return Response(status_code=HTTPStatus.OK)

    def run(self):
        """
        Sets up the server config and starts the uvicorn server on a new event loop
        """
        logger.debug(f"Server thread id: {threading.get_ident()}")
        self._server.run()

    def shutdown(self):
        """
        Shuts down the server by updating server properties.
        See `uvicorn.server.Server.main_loop` for more details
        """
        self._server.should_exit = True
        self._server.force_exit = True
