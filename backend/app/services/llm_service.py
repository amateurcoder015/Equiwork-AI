import json
import time
import requests
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()

# REPLACE WITH YOUR NEW TOKEN (Read Permission)
HF_TOKEN = os.getenv("HF_TOKEN")

# We use the raw API URL as a backup to ensure it always works
API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def ask_llm(prompt: str):
    print(f"🔹 [LLM] Sending Request...")
    
    # Method 1: Try the Python Client (Best for speed)
    try:
        client = InferenceClient(model="Qwen/Qwen2.5-7B-Instruct", token=HF_TOKEN)
        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500, 
            temperature=0.1
        )
        content = response.choices[0].message.content
        if content:
            print("✅ [LLM] Client Success!")
            return content.strip()
    except Exception as e:
        print(f"⚠️ [LLM Client Failed]: {e}")
        print("🔄 Switching to Raw API Fallback...")

    # Method 2: Raw Request (Failsafe)
    for attempt in range(3):
        try:
            payload = {
                "inputs": f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n",
                "parameters": {"max_new_tokens": 500, "return_full_text": False}
            }
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                # Raw API returns a list like [{'generated_text': '...'}]
                output = response.json()
                if isinstance(output, list) and 'generated_text' in output[0]:
                    print("✅ [LLM] Raw API Success!")
                    return output[0]['generated_text'].strip()
            else:
                print(f"⚠️ Raw API Error {response.status_code}: {response.text}")
                
            time.sleep(2)
        except Exception as e:
            print(f"❌ Raw Request Failed: {e}")
            
    return ""

def get_ai_complexity(task_title: str):
    """Parses JSON strictly from the AI response."""
    prompt = f"""
    You are a technical project manager.
    Task: {task_title}
    
    Output ONLY valid JSON with no markdown formatting:
    {{
        "complexity": <int 1-10>,
        "context_switch": <int 1-10>
    }}
    """
    res = ask_llm(prompt)
    try:
        clean_res = res.replace("```json", "").replace("```", "").strip()
        start = clean_res.find('{')
        end = clean_res.rfind('}') + 1
        return json.loads(clean_res[start:end])
    except:
        return {"complexity": 5, "context_switch": 5}