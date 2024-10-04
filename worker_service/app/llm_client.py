import requests
import os

LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://llm_service:8002/generate")

def get_llm_answer(question_text):
    try:
        response = requests.post(LLM_SERVICE_URL, json={"prompt": question_text})
        response.raise_for_status()
        data = response.json()
        answer = data.get("answer", "")
        return answer
    except Exception as e:
        print(f"Error contacting LLM service: {e}")
        return "Could not get an answer at this time."
