from sqlalchemy import Column, Integer, String, DateTime
from database import Base
import datetime


class Question(Base):
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    content = Column(String, nullable=False)
    create_date = Column(DateTime, default=datetime.datetime.now)
