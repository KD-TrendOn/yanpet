# api_service/app/schemas.py

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class QuestionCreate(BaseModel):
    question_text: str

class AnswerResponse(BaseModel):
    answer_text: str

class QuestionResponse(BaseModel):
    question_id: int
    answer_text: str
