from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from env import CyberTriageEnv, Action, Observation
from pydantic import BaseModel
import json

app = FastAPI(title="Cyber-Triage Scam Defender API")

# Add CORS middleware for Hugging Face Spaces compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize environment at startup
env = CyberTriageEnv()
current_obs = None

class ActionRequest(BaseModel):
    is_scam: bool
    confidence: float
    reasoning: str

@app.on_event("startup")
async def startup_event():
    global current_obs
    current_obs = env.reset()

@app.get("/reset")
def reset_env():
    """Reset the environment and return initial observation"""
    global current_obs
    try:
        current_obs = env.reset()
        # Return observation as dict
        obs_dict = current_obs.model_dump() if hasattr(current_obs, 'model_dump') else {
            'task_id': current_obs.task_id,
            'modality': current_obs.modality,
            'content': current_obs.content,
            'metadata': current_obs.metadata
        }
        return {
            "status": "success",
            "observation": obs_dict
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/step")
def step_env(action: ActionRequest):
    """Execute one step in the environment"""
    global current_obs
    try:
        act = Action(**action.model_dump())
        result = env.step(act)
        
        response = {
            "reward": result["reward"],
            "done": result["done"],
            "info": result["info"]
        }
        
        if result["observation"]:
            obs_dict = result["observation"].model_dump() if hasattr(result["observation"], 'model_dump') else {
                'task_id': result["observation"].task_id,
                'modality': result["observation"].modality,
                'content': result["observation"].content,
                'metadata': result["observation"].metadata
            }
            response["observation"] = obs_dict
            current_obs = result["observation"]
        else:
            response["observation"] = None
            
        return response
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/state")
def state_env():
    """Get current environment state"""
    return env.state()

@app.get("/")
def health_check():
    """Health check endpoint for Hugging Face Spaces"""
    return {"status": "ok", "service": "Cyber-Triage Scam Defender"}

@app.get("/health")
def health_detailed():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "Cyber-Triage Scam Defender API",
        "version": "1.0.0"
    }
