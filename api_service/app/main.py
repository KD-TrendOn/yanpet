from fastapi import FastAPI, Depends
from models import Question, Answer
from schemas import QuestionCreate, AnswerResponse
from database import async_session, init_db
from cache import get_redis_client
from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp
import json

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(question: QuestionCreate, session: AsyncSession = Depends(async_session)):
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
    async with aiohttp.ClientSession() as client:
        await client.post("http://worker_service:8001/process", json={"question_id": new_question.id})
    
    return AnswerResponse(answer_text="Your question is being processed. Please try again later.")
