import json
import time
from huggingface_hub import InferenceClient

# Replace with your actual Hugging Face Access Token
HF_TOKEN = "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"

# Using Qwen2.5-7B-Instruct: It's currently very reliable on HF free tier
client = InferenceClient(model="Qwen/Qwen2.5-7B-Instruct", token=HF_TOKEN)

def ask_llm(prompt: str):
    """Sends a prompt with retries to handle model loading (cold starts)."""
    for attempt in range(3):
        try:
            response = client.text_generation(
                prompt,
                max_new_tokens=500,
                temperature=0.1, # Lower temperature = more stable JSON
                return_full_text=False
            )
            if response.strip():
                return response.strip()
        except Exception as e:
            if "loading" in str(e).lower():
                time.sleep(5) # Wait for model to load
                continue
            print(f"HF API Error: {e}")
    return ""

def get_ai_complexity(task_title: str):
    """Parses JSON strictly from the AI response."""
    prompt = f"Task: {task_title}. Provide complexity (1-10) and context-switch (1-10). Response must be ONLY JSON: {{\"complexity\": 5, \"context_switch\": 3}}"
    res = ask_llm(prompt)
    try:
        # Look for the JSON block in case AI adds chatter
        start = res.find('{')
        end = res.rfind('}') + 1
        return json.loads(res[start:end])
    except:
        return {"complexity": 5, "context_switch": 5}