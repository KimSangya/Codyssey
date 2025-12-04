from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Question
from domain.question.question_schema import QuestionSchema

router = APIRouter(
    prefix='/api/question',
    tags=['question']
)


@router.get('/list', response_model=list[QuestionSchema])
def question_list(db: Session = Depends(get_db)):
    """DB에서 모든 질문을 조회"""
    questions = db.query(Question).order_by(Question.id.desc()).all()
    return questions
