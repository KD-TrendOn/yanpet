import os
from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://vllm_service:8000")
VLLM_API_KEY = os.getenv("VLLM_API_KEY", "token-abc123")

headers = {
    "Authorization": f"Bearer {VLLM_API_KEY}",
    "Content-Type": "application/json"
}

@app.post("/generate")
def generate_text(request: PromptRequest):
    payload = {
        "model": "Qwen/Qwen2.5-3B-Instruct",
        "messages": [{"role": "user", "content": request.prompt}]
    }
    response = requests.post(f"{VLLM_BASE_URL}/v1/chat/completions", json=payload, headers=headers)
    answer = response.json()["choices"][0]["message"]["content"]
    return {"answer": answer}
