from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class NodeStatus(str, Enum):
    HEALTHY = "healthy"
    OFFLINE = "offline"
    CORRUPTED = "corrupted"
    BREACHED = "breached"

class Action(BaseModel):
    action_type: str = Field(..., description="reboot, recalibrate, adjust_polling, quarantine, reconnect")
    node_id: int
    value: Optional[float] = None

class Observation(BaseModel):
    node_states: List[Dict[str, Any]]
    last_action_status: str
    error_logs: List[str]

class SensorFleetEnv:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.nodes = []
        self.action_history = []
        self.steps = 0
        self.nodes = self._initialize_nodes()

    def _get_obs(self):
        return Observation(
            node_states=self.nodes,
            last_action_status="ready",
            error_logs=[f"Node {n['id']} {n['status']}" for n in self.nodes if n["status"] != NodeStatus.HEALTHY]
        )

    def _initialize_nodes(self):
        nodes = []
        for i in range(6):
            nodes.append({
                "id": i,
                "status": NodeStatus.HEALTHY,
                "data_quality": "stable",
                "polling_rate": 5,
                "connection": "connected",
                "breach_timer": 0
            })
        if self.task_id == "TASK_EASY":
            nodes[1]["status"] = NodeStatus.OFFLINE
            nodes[2]["polling_rate"] = 2
        elif self.task_id == "TASK_MEDIUM":
            nodes[3]["status"] = NodeStatus.CORRUPTED
            nodes[4]["status"] = NodeStatus.OFFLINE
        elif self.task_id == "TASK_HARD":
            nodes[5]["status"] = NodeStatus.BREACHED
        return nodes

    def reset(self):
        self.nodes = self._initialize_nodes()
        self.action_history = []
        self.steps = 0
        return self._get_obs()

    def step(self, action: Action):
        self.steps += 1
        self.action_history.append({"node_id": action.node_id, "action_type": action.action_type})
        node = next((n for n in self.nodes if n["id"] == action.node_id), None)
        status = "failed"
        if node:
            if action.action_type == "reboot":
                node["status"] = NodeStatus.HEALTHY
                node["breach_timer"] = 0
                status = "success"
            elif action.action_type == "recalibrate":
                if self.task_id == "TASK_MEDIUM" and self.nodes[4]["status"] == NodeStatus.OFFLINE:
                    status = "blocked_by_dependency"
                else:
                    node["status"] = NodeStatus.HEALTHY
                    node["data_quality"] = "stable"
                    status = "success"
            elif action.action_type == "adjust_polling":
                node["polling_rate"] = int(action.value or 10)
                status = "success"
            elif action.action_type == "quarantine":
                node["connection"] = "isolated"
                status = "success"
            elif action.action_type == "reconnect":
                if node["status"] == NodeStatus.HEALTHY and node["connection"] == "isolated":
                    node["connection"] = "connected"
                    status = "success"
        for n in self.nodes:
            if n["status"] == NodeStatus.BREACHED:
                n["breach_timer"] += 1
                if n["breach_timer"] >= 3:
                    n["status"] = NodeStatus.OFFLINE
                    n["connection"] = "isolated"
                    n["breach_timer"] = 0
        return self._get_obs(), 0.0, self.steps >= 10, {"status": status}

    def state(self):
        return {"nodes": self.nodes, "action_history": self.action_history}
