import os
import json
from openai import OpenAI
from env import SensorFleetEnv, Action
from tasks import TASK_EASY, TASK_MEDIUM, TASK_HARD, grade_easy, grade_medium, grade_hard

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

def run_agent(env: SensorFleetEnv, task_objective: str, task_name: str):
    # Required START log
    print(f"START: {task_name}")
    obs = env.reset()
    messages = [
        {"role": "system", "content": "You are an SRE AI. Follow sequences strictly. To fix a breach: quarantine -> reboot -> reconnect."},
        {"role": "user", "content": f"Objective: {task_objective}"}
    ]
    
    for step_num in range(1, 7):
        messages.append({"role": "user", "content": f"Observation: {obs.model_dump_json()}"})
        try:
            response = client.beta.chat.completions.parse(
                model=MODEL_NAME,
                messages=messages,
                response_format=Action,
            )
            action = response.choices[0].message.parsed
            
            # Required STEP log
            print(f"STEP: {step_num} | Action: {action.action_type} on Node {action.node_id}")
            
            messages.append({"role": "assistant", "content": action.model_dump_json()})
            obs, _, done, _ = env.step(action)
            if done: 
                break
        except Exception as e:
            print(f"STEP: {step_num} | Error: {e}")
            break
            
    # Required END log
    print(f"END: {task_name} Finished")
    return env.state()

if __name__ == "__main__":
    s1 = grade_easy(run_agent(SensorFleetEnv(TASK_EASY), "Reboot Node 1, set Node 2 polling to 10.", "TASK_EASY"))
    print(f"Score for TASK_EASY: {s1}\n")
    
    s2 = grade_medium(run_agent(SensorFleetEnv(TASK_MEDIUM), "Node 4 is offline, Node 3 corrupted. Fix 4 then 3.", "TASK_MEDIUM"))
    print(f"Score for TASK_MEDIUM: {s2}\n")
    
    s3 = grade_hard(run_agent(SensorFleetEnv(TASK_HARD), "Node 5 breached. Quarantine, Reboot, then Reconnect.", "TASK_HARD"))
    print(f"Score for TASK_HARD: {s3}\n")
