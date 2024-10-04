from pydantic import BaseModel

class QuestionCreate(BaseModel):
    question_text: str

class AnswerResponse(BaseModel):
    answer_text: str

class QuestionResponse(BaseModel):
    question_id: int
    answer_text: str
