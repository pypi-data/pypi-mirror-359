import json
import pytest
import re

from hyperpod_elastic_agent.logagent.log_agent import LogState
from hyperpod_elastic_agent.server.server import AgentState
from hyperpod_elastic_agent.server.util import (StatusResponse,
                                                StatusResponseJSONEncoder)
from torch.distributed.elastic.agent.server import RunResult
from torch.distributed.elastic.agent.server.api import WorkerState
from torch.distributed.elastic.multiprocessing import ProcessFailure
from unittest.mock import Mock, mock_open, patch

TORCHELASTIC_ERROR_FILE = '''{
          "message": {
            "message": "RuntimeError: [../third_party/gloo/gloo/transport/tcp/pair.cc:534] Connection closed by peer",
            "extraInfo": {
              "py_callstack": "Traceback Connection closed by peer [192.168.65.3]:35304",
              "timestamp": "1730223202"
            }
          }
        }'''


class TestUtil:

    @classmethod
    def setup_class(cls):
        with patch("builtins.open",
                   new_callable=mock_open,
                   read_data=TORCHELASTIC_ERROR_FILE), patch(
                       "os.path.isfile", return_value=True):
            cls.proc_failure_0 = ProcessFailure(
                local_rank=0,
                pid=111,
                exitcode=1,
                error_file="/tmp/hyperpod/none_2o6jvae_/attempt_0/0/error.json",
            )
        cls.proc_failure_1 = ProcessFailure(
            local_rank=1,
            pid=123,
            exitcode=1,
            error_file="<N/A>",
        )
        cls.fail_run_result = RunResult(state=WorkerState.FAILED,
                                        failures={
                                            0: cls.proc_failure_0,
                                            1: cls.proc_failure_1
                                        },
                                        return_values={})
        cls.success_run_result = RunResult(state=WorkerState.SUCCEEDED,
                                           failures={},
                                           return_values={
                                               0: None,
                                               1: None
                                           })

    def test_success(self):
        status_resp = StatusResponse(
            status=AgentState.COMPLETED,
            log_state=LogState.HEALTHY,
            run_result=self.success_run_result,
            transitions={
                AgentState.READY: '2024-11-20T23:37:17.855065+00:00',
                AgentState.RUNNING: '2024-11-20T23:37:37.594312+00:00',
                AgentState.COMPLETED: '2024-11-20T23:38:08.703561+00:00',
            },
            agent_version="1.0.0",
            ip_version="2025-01-10T12:00:00Z",
        )
        resp_txt = json.dumps(status_resp, cls=StatusResponseJSONEncoder)
        expected = (
            r'\{"status": "completed", "transitions": \{'
            r'"READY": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}", '
            r'"RUNNING": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}", '
            r'"COMPLETED": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}"\}, '
            r'"ipversion": "2025-01-10T12:00:00Z", '
            r'"agent_version": "1.0.0"\}')
        assert re.fullmatch(expected, resp_txt) is not None

    def test_log_state_failure(self):
        status_resp = StatusResponse(
            status=AgentState.FAULTED,
            log_state=LogState.HANGING,
            run_result=self.fail_run_result,
            transitions={
                AgentState.READY: '2024-11-20T23:37:17.855065+00:00',
                AgentState.RUNNING: '2024-11-20T23:37:37.594312+00:00',
                AgentState.FAULTED: '2024-11-20T23:38:08.703561+00:00',
            },
            agent_version="1.0.0",
            log_rule_names=["dummy_rule_1", "dummy_rule_2"],
        )
        resp_txt = str(json.dumps(status_resp, cls=StatusResponseJSONEncoder))
        expected = (
            r'\{"status": "faulted", "transitions": \{'
            r'"READY": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}", '
            r'"RUNNING": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}", '
            r'"FAULTED": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}"\}, '
            r'"reason": "LogStateHanging_dummy_rule_1", "message": "\{.*\}", '
            r'"agent_version": "1.0.0"\}')
        assert re.fullmatch(expected, resp_txt) is not None
        assert r'\"log_rule_names\": [\n        \"dummy_rule_1\",\n        \"dummy_rule_2\"' in resp_txt

    def test_worker_state_failure(self):
        status_resp = StatusResponse(
            status=AgentState.FAULTED,
            log_state=LogState.HEALTHY,
            run_result=self.fail_run_result,
            transitions={
                AgentState.READY: '2024-11-20T23:37:17.855065+00:00',
                AgentState.RUNNING: '2024-11-20T23:37:37.594312+00:00',
                AgentState.FAULTED: '2024-11-20T23:38:08.703561+00:00',
            },
            agent_version="1.0.0",
            ip_version="2025-01-10T12:00:00Z",
        )
        resp_txt = str(json.dumps(status_resp, cls=StatusResponseJSONEncoder))
        expected = (
            r'\{"status": "faulted", "transitions": \{'
            r'"READY": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}", '
            r'"RUNNING": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}", '
            r'"FAULTED": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}"\}, '
            r'"reason": "WorkerStateFailed", "message": "\{.*\}", '
            r'"ipversion": "2025-01-10T12:00:00Z", '
            r'"agent_version": "1.0.0"\}')
        assert re.fullmatch(expected, resp_txt) is not None

    def test_incorrect_encoder(self):
        with pytest.raises(
                TypeError,
                match="Object of type Mock is not JSON serializable"):
            json.dumps(Mock(), cls=StatusResponseJSONEncoder)
