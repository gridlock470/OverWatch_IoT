# 🌐 OverWatch IoT: An OpenEnv RL Environment

> *In a fleet of 10,000 industrial IoT sensors, manual triage is impossible. OverWatch IoT provides a standardized sandbox to train AI agents to autonomously heal hardware before a system-wide blackout occurs.*

## 🚀 What is this?
OverWatch IoT is a fully compliant **OpenEnv** reinforcement learning environment. 

Instead of just testing an LLM's ability to chat, this environment tests an agent's ability to act as a **Site Reliability Engineer (SRE)**. It gives an AI agent a "body" to interact with a simulated fleet of IoT sensors that are prone to hardware failures, data corruption, and cyber breaches. 

By adhering to the Meta/Hugging Face OpenEnv standard, this project serves as a plug-and-play testing facility to evaluate the reasoning and planning capabilities of frontier AI models.

## 🛠️ The Environment Mechanics
The agent manages a localized network of 6 sensor nodes. It must read the state of the network and execute precise terminal commands to restore health.

**Possible AI Actions:**
* `reboot`: Restores an offline node.
* `recalibrate`: Fixes corrupted data streams.
* `adjust_polling`: Mitigates network lag.
* `quarantine`: Isolates a compromised node from the main network.
* `reconnect`: Restores network access to a clean, isolated node.

## 🧠 The Difficulty Curve (Tasks)
To properly benchmark an AI, the environment features a strict difficulty progression that tests multi-step reasoning and dependency awareness.

* **🟢 Task 1: Diagnosis (Easy)** The agent must identify two distinct issues simultaneously. Node 1 is offline, but Node 2 is simply lagging and requires a polling rate adjustment.
* **🟡 Task 2: Cascading Failure (Medium)** Simulates a hardware dependency. Node 3 is outputting corrupted data *because* Node 4 is offline. The AI must realize that recalibrating Node 3 will fail until Node 4 is successfully rebooted first.
* **🔴 Task 3: The Iron Curtain (Hard)** A security breach on Node 5. The agent must execute a strict, stateful sequence: **Quarantine -> Reboot -> Reconnect**. Any deviation from this protocol results in task failure.

## 💻 Technical Stack
* **Framework:** OpenEnv Standard
* **Containerization:** Docker & Uvicorn
* **API Routing:** FastAPI
* **Validation:** Pydantic strictly enforces inputs/outputs

## 🏃 How to Run Locally
Ensure you have the OpenEnv CLI installed, then simply point it to the environment:
`openenv run --env Grid470/OverWatch_IoT --task TASK_HARD`
