import json

from ..logagent.log_agent import LogState
from dataclasses import dataclass
from enum import Enum
from torch.distributed.elastic.agent.server import RunResult, WorkerState
from torch.distributed.elastic.multiprocessing import ProcessFailure
from typing import Dict, List, Optional


class AgentState(str, Enum):
    """
    READY - Agent is ready to receive commands from control plane
    RUNNING - Agent received a START job command
    COMPLETED - Training script succeeded
    FAULTED - Training script failed
    STOPPING - Agent received a `/stop` request from a RUNNING or FAULTED state.
               Once workers are stopped this will auto-transition to READY
    SHUTDOWN - Agent received a command to shut down
    """
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAULTED = "FAULTED"
    STOPPING = "STOPPING"
    SHUTDOWN = "SHUTDOWN"


VALID_TRANSITIONS = {
    AgentState.READY: [AgentState.RUNNING, AgentState.SHUTDOWN],
    AgentState.RUNNING: [
        AgentState.COMPLETED,
        AgentState.FAULTED,
        AgentState.STOPPING,
        AgentState.SHUTDOWN  # For testing only
    ],
    AgentState.FAULTED: [AgentState.STOPPING, AgentState.SHUTDOWN],
    AgentState.STOPPING: [AgentState.READY],  # Automated
    AgentState.COMPLETED: [AgentState.SHUTDOWN, AgentState.STOPPING],
    AgentState.SHUTDOWN: [],
}


@dataclass
class StatusResponse:
    status: str
    log_state: LogState
    run_result: RunResult
    transitions: Dict[AgentState, str]
    agent_version: str
    ip_version: Optional[str] = None
    log_rule_names: Optional[List[str]] = None


class StatusResponseJSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, StatusResponse):
            response = {
                "status": o.status.lower(),
                "transitions": o.transitions,
            }
            if o.log_state in {LogState.HANGING, LogState.SLOW}:
                response[
                    "reason"] = f"LogState{o.log_state.value.lower().capitalize()}_{o.log_rule_names[0]}"
                response["message"] = json.dumps(
                    {
                        "log_rule_names": o.log_rule_names,
                        "run_result": o.run_result,
                    },
                    indent=4,
                    cls=StatusResponseJSONEncoder,
                )
            elif o.run_result.state in {
                    WorkerState.UNHEALTHY, WorkerState.FAILED
            }:
                response[
                    "reason"] = f"WorkerState{o.run_result.state.value.lower().capitalize()}"
                response["message"] = json.dumps(
                    {
                        "run_result": o.run_result,
                    },
                    indent=4,
                    cls=StatusResponseJSONEncoder,
                )
            if o.ip_version:
                response["ipversion"] = o.ip_version
            if o.agent_version:
                response["agent_version"] = o.agent_version
            return response
        elif isinstance(o, RunResult):
            return o.__dict__
        elif isinstance(o, ProcessFailure):
            return o.__dict__
        return super().default(o)
