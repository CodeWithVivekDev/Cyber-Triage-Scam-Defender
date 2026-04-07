import os
import json
from openai import OpenAI
from env import CyberTriageEnv, Action

def run_inference():
    # Strict hackathon vars mappings
    api_base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-4o")
    hf_token = os.getenv("HF_TOKEN", "dummy")
    
    # Initialize OpenAPI specifically pointing to given parameters natively.
    client = OpenAI(
        base_url=api_base_url,
        api_key=hf_token
    )
    
    env = CyberTriageEnv()
    obs = env.reset()
    
    print("[START] Agent execution initiated.")
    
    total_reward = 0.0
    done = False
    
    while not done:
        print(f"[STEP] Task: {obs.task_id} | Modality: {obs.modality}")
        print(f"[STEP] Content: {obs.content}")
        
        system_prompt = (
            "You are a cybersecurity expert analyzing digital communications for signs of scams, phishing, or deepfakes. "
            "Examine the provided content and metadata. Return ONLY a JSON object exactly matching this schema: "
            "{\"is_scam\": boolean, \"confidence\": float, \"reasoning\": \"string\"}"
        )
        user_prompt = f"Modality: {obs.modality}\nContent: {obs.content}\nMetadata: {json.dumps(obs.metadata)}"
        
        try:
            # We strictly route the evaluation output via LLM to execute instructions as stated.
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={ "type": "json_object" },
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            action = Action(
                is_scam=result.get("is_scam", False),
                confidence=result.get("confidence", 0.5),
                reasoning=result.get("reasoning", "Fallback reasoning")
            )
        except Exception as e:
            # Fallback action if token/client fails in dummy local testing
            sys_fail = "URGENT" in obs.content or "wire money" in obs.content or "immediate transfer" in obs.content
            action = Action(is_scam=sys_fail, confidence=1.0, reasoning=f"API Fallback: Local rule matching.")
            
        print(f"[STEP] Agent decided -> Is Scam: {action.is_scam} | Confidence: {action.confidence}")
        print(f"[STEP] Reasoning: {action.reasoning}")
        
        step_result = env.step(action)
        reward = step_result["reward"]
        done = step_result["done"]
        obs = step_result["observation"]
        
        total_reward += reward
        print(f"[STEP] Action Reward: {reward} | Cumulative: {total_reward}")
        
    print(f"[END] Evaluation completed. Final Total Reward: {total_reward}")

if __name__ == "__main__":
    run_inference()
