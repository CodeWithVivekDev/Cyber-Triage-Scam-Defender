from fastapi import FastAPI
from env import CyberTriageEnv, Action
from pydantic import BaseModel

app = FastAPI(title="Cyber-Triage Scam Defender API")
env = CyberTriageEnv()

class ActionRequest(BaseModel):
    is_scam: bool
    confidence: float
    reasoning: str

@app.get("/reset")
def reset_env():
    obs = env.reset()
    return obs.model_dump()

@app.post("/step")
def step_env(action: ActionRequest):
    act = Action(**action.model_dump())
    result = env.step(act)
    if result["observation"]:
        result["observation"] = result["observation"].model_dump()
    return result

@app.get("/state")
def state_env():
    return env.state()

@app.get("/")
def health_check():
    """Hugging Face automated ping responder"""
    return {"status": "ok"}
