# api_service/app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.future import select
from models import Question, Answer, User
from schemas import QuestionCreate, AnswerResponse, QuestionResponse
from database import async_session, init_db, scoped_session_dependency
from cache import get_redis_client
from sqlalchemy.ext.asyncio import AsyncSession
from celery_app import celery_app
from auth import auth_router, get_user, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt

app = FastAPI()

app.include_router(auth_router, tags=["auth"])

@app.on_event("startup")
async def startup():
    await init_db()

from auth import oauth2_scheme

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(scoped_session_dependency)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Now token is correctly extracted from the Authorization header
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(session, username=username)
    if user is None:
        raise credentials_exception
    return user


@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(question: QuestionCreate, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(scoped_session_dependency)):
    redis = get_redis_client()
    cache_key = f"answer:{question.question_text}"

    cached_answer = await redis.get(cache_key)
    if cached_answer:
        return AnswerResponse(answer_text=cached_answer)

    new_question = Question(question_text=question.question_text, user_id=current_user.id)
    session.add(new_question)
    await session.commit()
    await session.refresh(new_question)

    # Send task to Celery
    celery_app.send_task('tasks.process_question', args=[new_question.id])

    return QuestionResponse(question_id=new_question.id, answer_text="Ваш вопрос обрабатывается. Пожалуйста, попробуйте позже.")

@app.get("/api/answer/{question_id}", response_model=AnswerResponse)
async def get_answer(question_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(scoped_session_dependency)):
    redis = get_redis_client()
    cache_key = f"answer:{question_id}"
    cached_answer = await redis.get(cache_key)
    if cached_answer:
        return AnswerResponse(answer_text=cached_answer)

    result = await session.execute(
        select(Answer).join(Question).where(Answer.question_id == question_id, Question.user_id == current_user.id)
    )
    answer = result.scalar_one_or_none()
    if answer:
        await redis.set(cache_key, answer.answer_text)
        return AnswerResponse(answer_text=answer.answer_text)
    else:
        return AnswerResponse(answer_text="Ответ еще не готов.")
