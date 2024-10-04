from fastapi import FastAPI, Depends
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from models import Question, Answer
from schemas import QuestionCreate, AnswerResponse, QuestionResponse
from database import async_session, init_db, scoped_session_dependency
from cache import get_redis_client
from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp
import json
from celery_app import celery_app  # Import the Celery app

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(question: QuestionCreate, session: AsyncSession = Depends(scoped_session_dependency)):
    redis = get_redis_client()
    cache_key = f"answer:{question.question_text}"

    cached_answer = await redis.get(cache_key)
    if cached_answer:
        return AnswerResponse(answer_text=cached_answer)

    new_question = Question(question_text=question.question_text)
    session.add(new_question)
    await session.commit()
    await session.refresh(new_question)
    
    # Send task to Celery
    celery_app.send_task('tasks.process_question', args=[new_question.id])
    
    return AnswerResponse(answer_text="Your question is being processed. Please try again later.")

@app.get("/api/answer/{question_id}", response_model=AnswerResponse)
async def get_answer(question_id: int, session: AsyncSession = Depends(async_session)):
    # Попытка получить ответ из кэша
    redis = get_redis_client()
    cache_key = f"answer:{question_id}"
    cached_answer = await redis.get(cache_key)
    if cached_answer:
        return AnswerResponse(answer_text=cached_answer)

    # Если в кэше нет, получаем из базы данных
    result = await session.execute(
        select(Answer).where(Answer.question_id == question_id)
    )
    answer = result.scalar_one_or_none()
    if answer:
        # Сохраняем в кэш
        await redis.set(cache_key, answer.answer_text)
        return AnswerResponse(answer_text=answer.answer_text)
    else:
        return AnswerResponse(answer_text="Ответ еще не готов.")