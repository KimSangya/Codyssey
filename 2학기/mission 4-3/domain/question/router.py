from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import SessionLocal
from models import Question

router = APIRouter(prefix='/questions', tags=['questions'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post('')
def create_question(subject: str, content: str, db: Session = Depends(get_db)):
    if not subject or not content:
        raise HTTPException(status_code=400, detail='subject와 content는 비워둘 수 없습니다.')
    q = Question(subject=subject, content=content, create_date=datetime.utcnow())
    db.add(q)
    db.commit()
    db.refresh(q)
    return {'message': 'created', 'question': {'id': q.id, 'subject': q.subject}}


@router.get('')
def list_questions(db: Session = Depends(get_db)):
    rows = db.query(Question).order_by(Question.id.desc()).all()
    data = [
        {
            'id': r.id,
            'subject': r.subject,
            'content': r.content,
            'create_date': r.create_date.isoformat()
        } for r in rows
    ]
    return {'items': data, 'count': len(data)}
