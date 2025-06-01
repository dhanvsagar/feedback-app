from email.policy import default

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres@localhost/feedback_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(String(30), nullable=False)
    message = Column(String(250), nullable=False)
    created_at = Column(DateTime, default=datetime.now())

def create_table():
    Base.metadata.create_all(bind=engine)


create_table()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()