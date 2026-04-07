import os
import json
from env import CyberTriageEnv, Action, Observation
from openai import OpenAI

class BaselineAgent:
    def __init__(self):
        # We need an open API key.
        self.client = OpenAI() # Requires OPENAI_API_KEY env var
        
    def act(self, obs: Observation) -> Action:
        system_prompt = (
            "You are a cybersecurity expert analyzing digital communications for signs of scams, phishing, or deepfakes. "
            "Examine the provided content and metadata. Return ONLY a JSON object exactly matching this schema: "
            "{\"is_scam\": boolean, \"confidence\": float (0.0 to 1.0), \"reasoning\": \"string\"}"
        )
        
        user_prompt = f"Modality: {obs.modality}\nContent: {obs.content}\nMetadata: {json.dumps(obs.metadata)}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={ "type": "json_object" },
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            return Action(
                is_scam=result["is_scam"],
                confidence=result["confidence"],
                reasoning=result["reasoning"]
            )
        except Exception as e:
            # Fallback action
            print(f"Error during OpenAI API call: {e}")
            return Action(is_scam=True, confidence=0.5, reasoning=f"Fallback due to error: {e}")

if __name__ == "__main__":
    env = CyberTriageEnv()
    
    if "OPENAI_API_KEY" not in os.environ:
        print("WARNING: OPENAI_API_KEY environment variable not set. The agent will likely fail or use fallbacks.")
        
    agent = BaselineAgent()
    
    print("Starting Cyber-Triage Evaluation...")
    obs = env.reset()
    total_reward = 0.0
    
    while True:
        print(f"\n--- Current Task: {obs.task_id} ({obs.modality}) ---")
        print(f"Content: {obs.content}")
        action = agent.act(obs)
        print(f"Agent Action -> Scam: {action.is_scam}, Confidence: {action.confidence:.2f}")
        print(f"Reasoning: {action.reasoning}")
        
        step_result = env.step(action)
        reward = step_result["reward"]
        total_reward += reward
        print(f"Reward received: {reward}")
        
        if step_result["done"]:
            break
        obs = step_result["observation"]
            
    print(f"\nEvaluation Complete! Total Reward: {total_reward}")
