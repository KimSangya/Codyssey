from fastapi import FastAPI
from domain.question.question_router import router as question_router
from database import Base, engine

# DB 테이블 생성 (승인된 Alembic으로도 가능하지만, 안전하게 유지)
Base.metadata.create_all(bind=engine)

app = FastAPI(title='Mars Board', version='1.0.0')


@app.get('/')
def root():
    return {'message': 'Board API up'}


app.include_router(question_router)
