from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
# worker_service/app/models.py


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # Added this line

class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_text = Column(String)
