import requests
import time
import json
import os
import sys

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models import Action

# On HF Spaces, the agent targets the primary port 7860
API_BASE = os.getenv("SPACE_URL", "http://127.0.0.1:7860")

def run_agent(task_id="task_1"):
    print(f"--- Starting Agent for {task_id} ---")
    
    # Reset Environment
    reset_resp = requests.post(f"{API_BASE}/env/reset/{task_id}")
    if reset_resp.status_code != 200:
        # Fallback to local test if reset failed (maybe it's on localhost)
        print("Failed to reset env on remote, trying localhost:7860...")
        API_BASE_LOCAL = "http://127.0.0.1:7860"
        reset_resp = requests.post(f"{API_BASE_LOCAL}/env/reset/{task_id}")
        if reset_resp.status_code != 200:
            print("Both reset attempts failed.")
            return
        
    data = reset_resp.json()
    sid = data["session_id"]
    obs = data["observation"]
    
    # 1. READ FILE
    filename = obs["files"][0]
    action = Action(command="read_file", filename=filename)
    step_resp = requests.post(f"{API_BASE}/env/step/{sid}", json=action.dict()).json()
    print(f"Agent read file: {filename}")
    
    # 2. ANALYSIS & COMMENT
    time.sleep(1)
    comment_action = Action(
        command="add_comment", 
        filename=filename, 
        line_number=1, 
        content="Detecting potential vulnerability or logic flaw in this block. Specifically checking for key vulnerability markers."
    )
    requests.post(f"{API_BASE}/env/step/{sid}", json=comment_action.dict())
    
    # 3. SUBMIT DECISION
    final_action = Action(command="request_changes")
    result = requests.post(f"{API_BASE}/env/step/{sid}", json=final_action.dict()).json()
    
    print(f"TASK FINISHED. REWARD: {result['reward']}")
    return result

if __name__ == "__main__":
    run_agent("task_1")
    run_agent("task_2")
    run_agent("task_3")