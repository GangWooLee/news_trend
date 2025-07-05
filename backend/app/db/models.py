from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.orm import declarative_base
from datetime import datetime
from backend.app.config import settings

Base = declarative_base()

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512), nullable=False)
    link = Column(String(1024), unique=True, nullable=False)
    originallink = Column(String(1024))
    description = Column(Text)
    pub_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# DB 초기화 함수

def init_db():
    engine = create_engine(settings.DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)