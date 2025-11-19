from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite:///./app.db'

# SQLite + FastAPI에서 다중 스레드 접근 허용
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False}
)

# autocommit=False, autoflush=False (요구사항)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 모델
Base = declarative_base()
