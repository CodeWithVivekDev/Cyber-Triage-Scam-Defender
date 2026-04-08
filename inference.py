import os
import json
import sys
from openai import OpenAI
from env import CyberTriageEnv, Action

def format_bool(b: bool) -> str:
    """Forces Python booleans to lowercase 'true' or 'false' for the auto-grader."""
    return str(b).lower()

def run_inference():
    # Strict hackathon vars mappings
    api_base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-4o")
    hf_token = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
    
    # Environment info
    benchmark_name = "codetitans-scam-defender"
    task_name = os.getenv("TASK_NAME", "cyber-triage") # Update this if your env has multiple tasks

    client = OpenAI(base_url=api_base_url, api_key=hf_token)
    
    env = CyberTriageEnv()
    obs = env.reset()
    
    # [START] STRICT FORMAT
    print(f"[START] task={task_name} env={benchmark_name} model={model_name}")
    
    done = False
    step_count = 0
    rewards_list = []
    error_msg = "null"
    
    while not done:
        step_count += 1
        error_msg = "null"
        
        # NOTE: If you want to debug, print to STDERR so the grader ignores it!
        # sys.stderr.write(f"Debug: Task {obs.task_id} | Modality: {obs.modality}\n")
        
        system_prompt = (
            "You are a cybersecurity expert analyzing digital communications for signs of scams, phishing, or deepfakes. "
            "Examine the provided content and metadata. Return ONLY a JSON object exactly matching this schema: "
            "{\"is_scam\": boolean, \"confidence\": float, \"reasoning\": \"string\"}"
        )
        # Handle potential dictionary access depending on your obs structure
        user_prompt = f"Modality: {getattr(obs, 'modality', 'unknown')}\nContent: {getattr(obs, 'content', '')}\nMetadata: {json.dumps(getattr(obs, 'metadata', {}))}"
        
        try:
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
            # Create a string representation of the action for the logger
            action_str = f"predict(is_scam={action.is_scam})"
            
            step_result = env.step(action)
            # Ensure we safely extract values regardless of if it's a dict or tuple
            if isinstance(step_result, dict):
                reward = step_result.get("reward", 0.0)
                done = step_result.get("done", True)
                obs = step_result.get("observation", obs)
            else:
                obs, reward, done, info = step_result
                
        except Exception as e:
            # Fallback action
            error_msg = str(e).replace('\n', ' ')
            # Fallback reasoning based on text match
            sys_fail = "URGENT" in getattr(obs, 'content', '') or "wire money" in getattr(obs, 'content', '')
            action = Action(is_scam=sys_fail, confidence=1.0, reasoning="API Fallback: Local rule matching.")
            action_str = f"fallback(is_scam={sys_fail})"
            
            # Assuming env.step works even if LLM fails
            try:
                obs, reward, done, info = env.step(action)
            except:
                reward = 0.00
                done = True

        rewards_list.append(reward)
        
        # [STEP] STRICT FORMAT (Only ONE per loop!)
        print(f"[STEP] step={step_count} action={action_str} reward={reward:.2f} done={format_bool(done)} error={error_msg}")
        
    # Final Score Calculation
    final_score = sum(rewards_list) / len(rewards_list) if rewards_list else 0.00
    is_success = final_score > 0.8 # You can adjust this threshold based on your rules
    rewards_str = ",".join([f"{r:.2f}" for r in rewards_list])
    
    # [END] STRICT FORMAT
    print(f"[END] success={format_bool(is_success)} steps={step_count} score={final_score:.2f} rewards={rewards_str}")

if __name__ == "__main__":
    run_inference()
