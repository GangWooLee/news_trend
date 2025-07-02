
# backend/app/services/crud.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.app.db.models import News
from backend.app.routers.schemas import NewsCreate
import logging
from typing import List

logger = logging.getLogger(__name__)

def create_news(db: Session, news_in: NewsCreate) -> News:
    news = News(**news_in.dict())
    db.add(news)
    try:
        db.commit()
        db.refresh(news)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to create news: {e}")
        raise
    return news

def get_news(db: Session, skip: int = 0, limit: int = 100) -> List[News]:
    return db.query(News).offset(skip).limit(limit).all()

def get_news_by_id(db: Session, news_id: int) -> News | None:
    return db.query(News).filter(News.id == news_id).first()

def delete_news(db: Session, news_id: int) -> bool:
    news = get_news_by_id(db, news_id)
    if not news:
        return False
    db.delete(news)
    db.commit()
    return True