import requests

def get_llm_answer(question_text):
    response = requests.post("http://llm_service:8002/generate", json={"prompt": question_text})
    return response.json().get("answer")
