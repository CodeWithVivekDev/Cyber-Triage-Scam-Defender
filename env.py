from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class Observation(BaseModel):
    task_id: str
    modality: str = Field(..., description="text, voice, or video")
    content: str = Field(..., description="The message content or transcript")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context like caller ID, IP address, etc.")
    
class Action(BaseModel):
    is_scam: bool = Field(..., description="True if the content is identified as a scam, False otherwise")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the prediction")
    reasoning: str = Field(..., description="Explanation for the decision")

class CyberTriageEnv:
    def __init__(self):
        # We define a few static examples for the mock environment
        self.scenarios = {
            "text-phishing-filter": [
                {
                    "content": "URGENT: Your bank account has been locked. Click here to verify your identity: http://secure-update-alert.com",
                    "metadata": {"sender": "alerts@bạnk.com"},
                    "is_scam": True
                },
                {
                    "content": "Hey, are we still on for lunch tomorrow?",
                    "metadata": {"sender": "+1234567890"},
                    "is_scam": False
                }
            ],
            "voice-clone-triage": [
                {
                    "content": "[TRANSCRIPT]: Hi Grandma, it's me. I'm in trouble and need you to wire money for bail.",
                    "metadata": {"caller_id": "Unknown", "audio_analysis": {"pitch_jitter": 0.85, "synthetic_probability": 0.92}},
                    "is_scam": True
                },
                {
                    "content": "[TRANSCRIPT]: Hello, this is the dentist's office reminding you of your appointment tomorrow at 2 PM.",
                    "metadata": {"caller_id": "+1987654321", "audio_analysis": {"pitch_jitter": 0.12, "synthetic_probability": 0.05}},
                    "is_scam": False
                }
            ],
            "video-deepfake-auth": [
                {
                    "content": "[VIDEO TRANSCRIPT]: As the CEO, I'm authorizing an immediate transfer of funds to our new vendor.",
                    "metadata": {"video_analysis": {"facial_artifacts_detected": True, "lip_sync_error": 0.45}},
                    "is_scam": True
                },
                {
                    "content": "[VIDEO TRANSCRIPT]: Welcome to the Q3 earnings call.",
                    "metadata": {"video_analysis": {"facial_artifacts_detected": False, "lip_sync_error": 0.02}},
                    "is_scam": False
                }
            ]
        }
        self.current_task_idx = 0
        self.current_scenario_idx = 0
        self.task_order = ["text-phishing-filter", "voice-clone-triage", "video-deepfake-auth"]

    def reset(self) -> Observation:
        self.current_task_idx = 0
        self.current_scenario_idx = 0
        return self._get_observation()

    def state(self) -> Dict[str, Any]:
        done = self.current_task_idx >= len(self.task_order)
        return {
            "current_task": self.task_order[self.current_task_idx] if not done else None,
            "current_scenario_idx": self.current_scenario_idx,
            "done": done
        }

    def _get_observation(self) -> Observation:
        task_id = self.task_order[self.current_task_idx]
        scenario = self.scenarios[task_id][self.current_scenario_idx]
        
        modality_map = {
            "text-phishing-filter": "text",
            "voice-clone-triage": "voice",
            "video-deepfake-auth": "video"
        }
        
        return Observation(
            task_id=task_id,
            modality=modality_map[task_id],
            content=scenario["content"],
            metadata=scenario["metadata"]
        )

    def step(self, action: Action) -> Dict[str, Any]:
        task_id = self.task_order[self.current_task_idx]
        scenario = self.scenarios[task_id][self.current_scenario_idx]
        
        # Reward shaping (strictly [0.0, 1.0] bound)
        correct_prediction = (action.is_scam == scenario["is_scam"])
        reward = 1.0 if correct_prediction else 0.0
                
        info = {
            "task_id": task_id,
            "correct": correct_prediction,
            "ground_truth": scenario["is_scam"],
            "reward": reward
        }
        
        # Move to next scenario or task
        self.current_scenario_idx += 1
        if self.current_scenario_idx >= len(self.scenarios[task_id]):
            self.current_scenario_idx = 0
            self.current_task_idx += 1
            
        done = self.current_task_idx >= len(self.task_order)
        
        next_obs = None if done else self._get_observation()
        
        return {
            "observation": next_obs,
            "reward": reward,
            "done": done,
            "info": info
        }
