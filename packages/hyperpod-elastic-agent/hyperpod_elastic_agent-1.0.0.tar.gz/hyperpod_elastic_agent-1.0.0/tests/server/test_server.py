import json
import pytest

from hyperpod_elastic_agent.logagent import LogState
from hyperpod_elastic_agent.server import AgentState, HyperPodElasticAgentServer
from fastapi.testclient import TestClient
from http import HTTPStatus
from torch.distributed.elastic.agent.server import RunResult
from torch.distributed.elastic.agent.server.api import WorkerState
from unittest.mock import Mock, patch

AGENT_STATE_TRANSITIONS = {
    AgentState.READY: '2024-11-20T23:37:17.855065+00:00',
    AgentState.RUNNING: '2024-11-20T23:37:37.594312+00:00',
    AgentState.COMPLETED: '2024-11-20T23:38:08.703561+00:00',
}


class TestHyperPodElasticAgentServer:

    @classmethod
    def setup_class(cls):
        cls.server_specs = {
            "host": "127.0.0.1",
            "port": 8000,
            "log_level": "info",
        }

    @pytest.fixture
    def mock_thread(self):
        patched_thread = patch('threading.Thread')
        patched_thread.start = Mock()
        return patched_thread

    @pytest.fixture
    def mock_agent(self):
        mock_agent = Mock()
        mock_agent.set_agent_state = Mock()
        mock_agent.get_run_result = Mock(return_value=RunResult(
            state=WorkerState.INIT))
        mock_agent.get_agent_state_info = Mock(
            return_value=(AgentState.READY, AGENT_STATE_TRANSITIONS,
                          "2025-01-10T12:00:00Z"))
        mock_agent.get_log_agent_state = Mock(return_value=(LogState.WAITING,
                                                            None))
        mock_agent.version = "1.0.0"
        return mock_agent

    @pytest.fixture
    def mock_app(self, mock_thread, mock_agent):
        with patch('threading.Thread', return_value=mock_thread):
            server = HyperPodElasticAgentServer(mock_agent, self.server_specs)
            return server._app

    @pytest.fixture
    def mock_server(self, mock_agent):
        server = HyperPodElasticAgentServer(mock_agent, self.server_specs)
        server._server.run = Mock()
        yield server

    @pytest.fixture
    def client(self, mock_app):
        return TestClient(mock_app)

    def test_register_routes(self, mock_app):
        assert mock_app.routes

    def test_api_start(self, client, mock_agent):
        rank_ips = [
            {
                'ip': '192.168.111.1',
                'rank': 0,
            },
            {
                'ip': '192.168.111.2',
                'rank': 1,
            },
        ]
        response = client.post("/start",
                               content=json.dumps({
                                   "rank": 0,
                                   "nnodes": 1,
                                   "faultCount": 33,
                                   "master_addr": "192.168.111.1",
                                   "master_port": "23456",
                                   "ipVersion": "2025-01-10T12:00:00Z",
                                   "rankIps": rank_ips,
                               }))
        assert response.status_code == HTTPStatus.OK
        mock_agent.set_agent_state.assert_called_once_with(AgentState.RUNNING)
        mock_agent.update_rendezvous_info.assert_called_once_with(
            0,
            1,
            33,
            "192.168.111.1",
            23456,
            "2025-01-10T12:00:00Z",
            rank_ips,
        )

    def test_api_start_incorrect_data(self, client, mock_agent):
        response = client.post("/start",
                               content=json.dumps({
                                   "rank": "invalid_rank",
                                   "nnodes": 1,
                               }))
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "invalid literal for int() with base 10: 'invalid_rank'" == response.json(
        )
        mock_agent.set_agent_state.assert_not_called()

    def test_api_stop(self, client, mock_agent):
        response = client.post("/stop")
        assert response.status_code == HTTPStatus.OK
        mock_agent.set_agent_state.assert_called_once_with(AgentState.STOPPING)

    def test_api_status(self, client, mock_agent):
        response = client.get("/status")
        assert response.status_code == HTTPStatus.OK
        assert json.loads(response.content) == {
            'status': 'ready',
            'transitions': AGENT_STATE_TRANSITIONS,
            'ipversion': '2025-01-10T12:00:00Z',
            'agent_version': '1.0.0'
        }
        mock_agent.get_run_result.assert_called_once()
        mock_agent.get_agent_state_info.assert_called_once()

    def test_api_shutdown(self, client, mock_agent):
        response = client.post("/shutdown")
        assert response.status_code == HTTPStatus.OK
        mock_agent.set_agent_state.assert_called_once_with(AgentState.SHUTDOWN)

    def test_server_run(self, mock_server):
        mock_server.start()
        mock_server._server.run.assert_called_once()

    def test_server_shutdown(self, mock_server):
        mock_server.shutdown()
        assert mock_server._server.should_exit
        assert mock_server._server.force_exit
