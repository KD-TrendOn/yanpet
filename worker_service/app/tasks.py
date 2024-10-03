from celery import Celery
from models import Question, Answer
from database import async_session
from llm_client import get_llm_answer
from cache import get_redis_client

app = Celery('tasks', broker='pyamqp://guest@rabbitmq//')

@app.task
def process_question(question_id):
    session = async_session()
    question = session.get(Question, question_id)
    answer_text = get_llm_answer(question.question_text)

    new_answer = Answer(question_id=question_id, answer_text=answer_text)
    session.add(new_answer)
    session.commit()

    # Cache the answer
    redis = get_redis_client()
    cache_key = f"answer:{question.question_text}"
    redis.set(cache_key, answer_text)
