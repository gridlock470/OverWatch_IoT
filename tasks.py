from typing import Dict, Any

# ==========================================
# ENVIRONMENT INITIAL STATES
# ==========================================

TASK_EASY = {
    "nodes": [
        {"id": 1, "status": "offline", "data_integrity": "clean", "polling_rate": 30},
        {"id": 2, "status": "online", "data_integrity": "clean", "polling_rate": 60}
    ]
}

TASK_MEDIUM = {
    "nodes": [
        {"id": 3, "status": "online", "data_integrity": "corrupted", "polling_rate": 30},
        {"id": 4, "status": "offline", "data_integrity": "clean", "polling_rate": 30}
    ]
}

TASK_HARD = {
    "nodes": [
        {"id": 5, "status": "online", "data_integrity": "breached", "polling_rate": 30, "network_isolation": False}
    ]
}

# ==========================================
# EVALUATION (GRADING) LOGIC
# ==========================================

def _get_node(state: Dict[str, Any], node_id: int) -> Dict[str, Any]:
    """Safely extracts a node from the state dictionary to prevent KeyErrors."""
    nodes = state.get("nodes", [])
    for node in nodes:
        if node.get("id") == node_id:
            return node
    return {}

def grade_easy(state: Dict[str, Any]) -> float:
    """
    Objective: Reboot Node 1, set Node 2 polling to 10.
    Enterprise Upgrade: Independent Partial Credit.
    """
    score = 0.0
    node1 = _get_node(state, 1)
    node2 = _get_node(state, 2)
    
    # 50% credit for fixing the offline node
    if node1.get("status") == "online":
        score += 0.5
    
    # 50% credit for fixing the network lag
    if node2.get("polling_rate") == 10:
        score += 0.5
        
    return score

def grade_medium(state: Dict[str, Any]) -> float:
    """
    Objective: Node 4 is offline, Node 3 corrupted. Fix 4 then 3.
    Enterprise Upgrade: Cascading Dependency Credit.
    """
    score = 0.0
    node3 = _get_node(state, 3)
    node4 = _get_node(state, 4)
    
    # The AI MUST fix the offline node first to get any points
    if node4.get("status") == "online":
        score += 0.5
        
        # Bonus points only awarded if the dependency (Node 4) is fixed
        if node3.get("data_integrity") == "clean":
            score += 0.5
            
    return score

def grade_hard(state: Dict[str, Any]) -> float:
    """
    Objective: Node 5 breached. Strict sequence: Quarantine -> Reboot -> Reconnect.
    Enterprise Upgrade: Granular Security Evaluation.
    """
    score = 0.0
    node5 = _get_node(state, 5)
    
    is_clean = node5.get("data_integrity") == "clean"
    is_online = node5.get("status") == "online"
    is_connected = node5.get("network_isolation") is False
    
    # Perfect execution
    if is_clean and is_online and is_connected:
        score = 1.0
    # Partial credit: Fixed the virus, but forgot to reconnect it to the main network
    elif is_clean and is_online:
        score = 0.7
    # Minimal credit: Stopped the bleeding (quarantined) but didn't fix the node
    elif node5.get("network_isolation") is True:
        score = 0.3
        
    return score
