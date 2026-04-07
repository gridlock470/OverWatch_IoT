import uvicorn
from fastapi import FastAPI
from env import SensorFleetEnv, Action
from tasks import TASK_EASY

app = FastAPI(title="IoT Sensor Triage OpenEnv")

# Default environment for the bot to hit
current_env = SensorFleetEnv(TASK_EASY)

@app.get("/")
def ping():
    return {"status": "200 OK", "message": "IoT Sensor Triage OpenEnv Ready"}

@app.post("/reset")
def reset_env():
    obs = current_env.reset()
    return obs.model_dump()

@app.post("/step")
def step_env(action: Action):
    obs, reward, done, info = current_env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state")
def get_state():
    return current_env.state()

# --- The exact main() block the validator is demanding ---
def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()