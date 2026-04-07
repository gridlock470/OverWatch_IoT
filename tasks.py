TASK_EASY = "TASK_EASY"
TASK_MEDIUM = "TASK_MEDIUM"
TASK_HARD = "TASK_HARD"

def grade_easy(state):
    score = 0.0
    nodes = state["nodes"]
    if nodes[1]["status"] == "healthy": score += 0.5
    if nodes[2]["polling_rate"] == 10: score += 0.5
    return score

def grade_medium(state):
    nodes = state["nodes"]
    if nodes[4]["status"] == "offline": return 0.0
    score = 0.0
    if nodes[4]["status"] == "healthy": score += 0.5
    if nodes[3]["status"] == "healthy": score += 0.5
    return score

def grade_hard(state):
    history = [a["action_type"] for a in state["action_history"] if a["node_id"] == 5]
    required = ["quarantine", "reboot", "reconnect"]
    idx = 0
    for action in history:
        if idx < len(required) and action == required[idx]:
            idx += 1
    if idx == 3: return 1.0
    if idx == 2: return 0.5
    if idx == 1: return 0.2
    return 0.0
