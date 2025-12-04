from pydantic import BaseModel
from datetime import datetime


class QuestionSchema(BaseModel):
    id: int
    subject: str
    content: str
    create_date: datetime

    class Config:
        orm_mode = True    # 보너스 과제 테스트 용
