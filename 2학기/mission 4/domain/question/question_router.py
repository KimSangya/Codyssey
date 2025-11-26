from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Question

router = APIRouter(
    prefix='/api/question',
    tags=['question']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/list')
def question_list(db: Session = Depends(get_db)):
    """SQLite에 저장된 질문 목록을 ORM으로 가져오는 함수"""
    questions = db.query(Question).order_by(Question.id.desc()).all()
    result = [
        {
            'id': q.id,
            'subject': q.subject,
            'content': q.content,
            'create_date': q.create_date.isoformat()
        }
        for q in questions
    ]
    return {'items': result, 'count': len(result)}
