import os
from openai import OpenAI
from env import SensorFleetEnv, Action
from tasks import TASK_EASY, TASK_MEDIUM, TASK_HARD, grade_easy, grade_medium, grade_hard

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

def clamp_score(score):
    return max(0.01, min(0.99, float(score)))

def run_agent(env: SensorFleetEnv, task_objective: str, task_name: str):
    print(f"[START] task={task_name}", flush=True)
    obs = env.reset()
    messages = [
        {"role": "system", "content": "You are an SRE AI. Follow sequences strictly. To fix a breach: quarantine -> reboot -> reconnect."},
        {"role": "user", "content": f"Objective: {task_objective}"}
    ]
    
    step_num = 0
    for i in range(1, 7):
        step_num = i
        messages.append({"role": "user", "content": f"Observation: {obs.model_dump_json()}"})
        try:
            response = client.beta.chat.completions.parse(
                model=MODEL_NAME,
                messages=messages,
                response_format=Action,
            )
            action = response.choices[0].message.parsed
            messages.append({"role": "assistant", "content": action.model_dump_json()})
            
            obs, reward, done, _ = env.step(action)
            
            safe_reward = clamp_score(reward)
            print(f"[STEP] step={step_num} reward={safe_reward}", flush=True)
            
            if done:
                break
        except Exception:
            print(f"[STEP] step={step_num} reward=0.01", flush=True)
            break
            
    return env.state(), step_num

if __name__ == "__main__":
    state1, steps1 = run_agent(SensorFleetEnv(TASK_EASY), "Reboot Node 1, set Node 2 polling to 10.", "TASK_EASY")
    score1 = clamp_score(grade_easy(state1))
    print(f"[END] task=TASK_EASY score={score1} steps={steps1}", flush=True)
    
    state2, steps2 = run_agent(SensorFleetEnv(TASK_MEDIUM), "Node 4 is offline, Node 3 corrupted. Fix 4 then 3.", "TASK_MEDIUM")
    score2 = clamp_score(grade_medium(state2))
    print(f"[END] task=TASK_MEDIUM score={score2} steps={steps2}", flush=True)
    
    state3, steps3 = run_agent(SensorFleetEnv(TASK_HARD), "Node 5 breached. Quarantine, Reboot, then Reconnect.", "TASK_HARD")
    score3 = clamp_score(grade_hard(state3))
    print(f"[END] task=TASK_HARD score={score3} steps={steps3}", flush=True)
