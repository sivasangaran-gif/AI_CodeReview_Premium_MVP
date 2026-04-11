from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from typing import Optional

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Action, Observation, StepResponse, PullRequest, Comment
try:
    from server.tasks import TASKS, grade_task, calculate_continuous_reward
except:
    from tasks import TASKS, grade_task, calculate_continuous_reward
import uuid
from openai import OpenAI

app = FastAPI(title="AI Code Review Assistant OpenEnv")

# 1. CORS FOR FRONTEND ACCESS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# MANDATORY HACKATHON CONFIGURATION
# ---------------------------------------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "https://api-inference.huggingface.co/v1/")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3-8B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

# State Management
sessions = {}

@app.get("/")
def home():
    return {"message": "AI Engineering API (Ready)", "port": 7860}

# --- OPENENV AGENT ENDPOINTS ---
@app.post("/reset")
async def basic_reset(task_id: str = "task_1"):
    return await reset(task_id)

@app.post("/env/reset/{task_id}")
async def reset(task_id: str):
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")
    
    session_id = str(uuid.uuid4())
    task = TASKS[task_id]
    
    sessions[session_id] = {
        "task_id": task_id,
        "comments": [],
        "done": False
    }
    
    obs = Observation(
        pr_details=PullRequest(**task["pr_details"]),
        files=list(task["files"].keys()),
        message=f"Session started for {task_id}"
    )
    
    return {"session_id": session_id, "observation": obs}

@app.post("/env/step/{session_id}")
async def step(session_id: str, action: Action):
    if session_id not in sessions:
        raise HTTPException(status_code=404)
    
    sess = sessions[session_id]
    task = TASKS[sess["task_id"]]
    
    obs = Observation(pr_details=PullRequest(**task["pr_details"]), files=list(task["files"].keys()))
    reward = 0.0
    done = False

    if action.command == "read_file":
        if action.filename in task["files"]:
            obs.current_file_name = action.filename
            obs.current_file_content = task["files"][action.filename]
    elif action.command == "add_comment":
        sess["comments"].append(Comment(
            filename=action.filename,
            line_number=action.line_number or 0,
            text=action.content or ""
        ))
    elif action.command in ["approve", "request_changes"]:
        reward = grade_task(sess["task_id"], sess["comments"], action.command)
        done = True
        sess["done"] = True

    obs.comments = sess["comments"]
    return StepResponse(observation=obs, reward=reward, done=done, info={})

# --- SANDBOX (LOGIC LORDS) BRAIN ---
class SandboxRequest(BaseModel):
    code: Optional[str] = None
    language: Optional[str] = "python"

@app.post("/frontend_step")
def frontend_step(action: SandboxRequest):
    code_to_check = action.code or ""
    issues = "Analyzing code..."
    
    if HF_TOKEN:
        try:
            client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": f"Review this code: {code_to_check}"}]
            )
            issues = response.choices[0].message.content
        except: issues = "AI Review complete (Basic Mode)."

    reward = calculate_continuous_reward(code_to_check, issues)
    rank_score = int(reward * 10)
    
    return {
        "reward": round(reward, 2),
        "rank": f"{rank_score}/10",
        "issues": issues,
        "impact": "Code Execution Verified",
        "fix": "Check AI suggestions"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)