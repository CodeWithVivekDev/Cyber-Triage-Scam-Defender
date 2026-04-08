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
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN") or os.getenv("API_KEY")
    
    # Environment info
    benchmark_name = "codetitans-scam-defender"
    task_name = os.getenv("TASK_NAME", "cyber-triage")

    # Initialize client with proper error handling
    try:
        if api_key:
            client = OpenAI(base_url=api_base_url, api_key=api_key)
        else:
            client = OpenAI()  # Will use OPENAI_API_KEY from environment
    except Exception as e:
        sys.stderr.write(f"Warning: Could not initialize OpenAI client: {e}\n")
        client = None
    
    try:
        env = CyberTriageEnv()
        obs = env.reset()
    except Exception as e:
        print(f"[ERROR] Failed to initialize environment: {e}")
        sys.exit(1)
    
    # [START] STRICT FORMAT
    print(f"[START] task={task_name} env={benchmark_name} model={model_name}")
    
    done = False
    step_count = 0
    rewards_list = []
    error_msg = "null"
    
    while not done:
        step_count += 1
        error_msg = "null"
        
        # Extract observation fields safely
        modality = getattr(obs, 'modality', 'unknown')
        content = getattr(obs, 'content', '')
        metadata = getattr(obs, 'metadata', {})
        
        # sys.stderr.write(f"Debug: Step {step_count} | Task: {getattr(obs, 'task_id', '?')} | Modality: {modality}\n")
        
        system_prompt = (
            "You are a cybersecurity expert analyzing digital communications for signs of scams, phishing, or deepfakes. "
            "Examine the provided content and metadata. Return ONLY a JSON object exactly matching this schema: "
            "{\"is_scam\": boolean, \"confidence\": float, \"reasoning\": \"string\"}"
        )
        user_prompt = f"Modality: {modality}\nContent: {content}\nMetadata: {json.dumps(metadata)}"
        
        try:
            if client is None:
                raise Exception("OpenAI client not initialized - no API key available")
                
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            action = Action(
                is_scam=result.get("is_scam", False),
                confidence=result.get("confidence", 0.5),
                reasoning=result.get("reasoning", "Fallback reasoning")
            )
            action_str = f"predict(is_scam={format_bool(action.is_scam)})"
            
        except Exception as e:
            # Fallback action using simple heuristics
            error_msg = str(e).replace('\n', ' ').replace('"', "'")
            
            # Simple fallback heuristics
            content_upper = content.upper()
            sys_fail = ("URGENT" in content_upper or 
                       "WIRE MONEY" in content_upper or 
                       "VERIFY" in content_upper or
                       "CLICK HERE" in content_upper or
                       "CONFIRM" in content_upper)
            
            action = Action(
                is_scam=sys_fail,
                confidence=1.0,
                reasoning="Fallback: Local rule matching (API error)"
            )
            action_str = f"fallback(is_scam={format_bool(sys_fail)})"

        try:
            step_result = env.step(action)
            
            # Handle both dict and tuple returns for flexibility
            if isinstance(step_result, dict):
                reward = step_result.get("reward", 0.0)
                done = step_result.get("done", False)
                obs = step_result.get("observation", obs)
            else:
                # Tuple unpacking fallback
                obs, reward, done, info = step_result
                
        except Exception as e:
            error_msg = str(e).replace('\n', ' ').replace('"', "'")
            reward = 0.0
            done = True

        rewards_list.append(reward)
        
        # [STEP] STRICT FORMAT (exactly one per loop iteration)
        print(f"[STEP] step={step_count} action={action_str} reward={reward:.2f} done={format_bool(done)} error={error_msg}")
        
    # Final Score Calculation
    final_score = sum(rewards_list) / len(rewards_list) if rewards_list else 0.0
    is_success = final_score > 0.5  # Adjusted threshold for robustness
    rewards_str = ",".join([f"{r:.2f}" for r in rewards_list])
    
    # [END] STRICT FORMAT
    print(f"[END] success={format_bool(is_success)} steps={step_count} score={final_score:.2f} rewards={rewards_str}")

if __name__ == "__main__":
    run_inference()
