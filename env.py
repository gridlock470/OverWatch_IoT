import copy
from typing import List, Dict, Any, Literal, Optional
from pydantic import BaseModel, Field

# ==========================================
# PYDANTIC SCHEMAS (AI Input/Output Validation)
# ==========================================

class NodeState(BaseModel):
    id: int
    status: str
    data_integrity: str
    polling_rate: int
    # Defaults to False so it doesn't crash on Easy/Medium tasks that omit it
    network_isolation: bool = False 

class FleetState(BaseModel):
    nodes: List[NodeState]

class Action(BaseModel):
    action_type: Literal["reboot", "recalibrate", "adjust_polling", "quarantine", "reconnect"] = Field(
        description="The exact SRE command to execute on the node."
    )
    node_id: int = Field(
        description="The ID of the sensor node to target."
    )
    value: Optional[int] = Field(
        default=None, 
        description="Numeric value for commands like adjust_polling (e.g., 10)."
    )

# ==========================================
# ENVIRONMENT PHYSICS & LOGIC
# ==========================================

class SensorFleetEnv:
    def __init__(self, initial_state: Dict[str, Any]):
        # Validate the raw task dictionary into a strictly typed Pydantic model
        self.initial_state = FleetState(**initial_state)
        # Deep copy ensures we don't accidentally corrupt the base tasks during the run
        self.current_state = self.initial_state.model_copy(deep=True)
        self.step_count = 0
        self.max_steps = 6

    def reset(self) -> FleetState:
        """Resets the environment back to a clean slate."""
        self.current_state = self.initial_state.model_copy(deep=True)
        self.step_count = 0
        return self.current_state

    def state(self) -> Dict[str, Any]:
        """Returns the raw dictionary format for tasks.py to grade."""
        return self.current_state.model_dump()

    def step(self, action: Action):
        self.step_count += 1
        reward = 0.0
        
        # Safely find the target node without risking a KeyError
        target_node = next((n for n in self.current_state.nodes if n.id == action.node_id), None)
        
        if not target_node:
            # The AI hallucinated a node ID that doesn't exist. Penalize and continue.
            return self.current_state, -0.1, self.step_count >= self.max_steps, {"error": "Node not found"}

        # ==========================================
        # STATE TRANSITIONS (Strict SRE Rules)
        # ==========================================
        
        if action.action_type == "reboot":
            target_node.status = "online"
            reward = 0.1
            
        elif action.action_type == "recalibrate":
            # DEPENDENCY CHECK: Cannot fix software on offline hardware
            if target_node.status == "online":
                target_node.data_integrity = "clean"
                reward = 0.1
            else:
                reward = -0.1 # Penalty for ignoring hardware dependencies
                
        elif action.action_type == "adjust_polling":
            if action.value is not None:
                target_node.polling_rate = action.value
                reward = 0.1
                
        elif action.action_type == "quarantine":
            target_node.network_isolation = True
            reward = 0.1
            
        elif action.action_type == "reconnect":
            # SECURITY CHECK: Connecting a breached node causes massive penalties
            if target_node.data_integrity == "clean":
                target_node.network_isolation = False
                reward = 0.1
            else:
                reward = -0.3 # Massive penalty for risking system integrity

        done = self.step_count >= self.max_steps
        return self.current_state, reward, done, {}
