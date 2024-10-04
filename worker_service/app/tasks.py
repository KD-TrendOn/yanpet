from models import Question, Answer
from database import SessionLocal, engine
from llm_client import get_llm_answer
from cache import get_redis_client
from sqlalchemy.orm import Session

from celery import Celery
import os

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest@rabbitmq//")

app = Celery('worker_service', broker=CELERY_BROKER_URL)

# Ensure all tables are created (if not already done)
# You might not need this if migrations are handled elsewhere
from database import Base
Base.metadata.create_all(bind=engine)

@app.task(name='tasks.process_question')
def process_question(question_id):
    # Create a new database session
    session = SessionLocal()
    try:
        # Query the question
        question = session.query(Question).filter(Question.id == question_id).first()
        if question is None:
            print(f"Question with id {question_id} not found.")
            return

        # Get the answer from the LLM service
        answer_text = get_llm_answer(question.question_text)

        # Create a new answer record
        new_answer = Answer(question_id=question_id, answer_text=answer_text)
        session.add(new_answer)
        session.commit()

        # Cache the answer
        redis = get_redis_client()
        cache_key = f"answer:{question.question_text}"
        redis.set(cache_key, answer_text)
    except Exception as e:
        print(f"An error occurred while processing question {question_id}: {e}")
        session.rollback()
    finally:
        # Close the session
        session.close()
