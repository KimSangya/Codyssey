from fastapi import FastAPI
from domain.question.router import router as question_router

app = FastAPI(title='Mars Board', version='1.0.0')

@app.get('/')
def root():
    return {'message': 'Board API up'}

# 라우터 등록
app.include_router(question_router)
