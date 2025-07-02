from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict

from backend.app.services.scraper import (
    fetch_news, fetch_news_by_rss
)
from backend.app.services.crud import (
    create_news, get_news, get_news_by_id, delete_news
)
from backend.app.routers.schemas import NewsCreate, NewsRead
from backend.app.db.session import get_db

router = APIRouter(prefix="/news", tags=["news"])

# 1) 키워드 검색 (GET /news/search)
@router.get("/search", response_model=List[Dict])
async def search_news(
    q: str = Query(..., description="검색 키워드"),
    display: int = Query(10, ge=1, le=100),
    start: int = Query(1, ge=1),
    sort: str = Query("date", regex="^(date|sim)$")
) -> List[Dict]:
    try:
        return fetch_news(query=q, display=display, start=start, sort=sort)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

# 2) 전체 뉴스 RSS (GET /news/rss)
@router.get("/rss", response_model=List[Dict])
async def get_rss(
    limit: int = Query(10, ge=1, le=100)
) -> List[Dict]:
    return fetch_news_by_rss(max_articles=limit)

# 3) CRUD: 단일 저장 (POST /news/)
@router.post("/", response_model=NewsRead)
async def add_news(
    news_in: NewsCreate,
    db: Session = Depends(get_db)
) -> NewsRead:
    return create_news(db, news_in)

# 4) CRUD: 일괄 저장 (POST /news/bulk)
@router.post("/bulk", response_model=List[NewsRead])
async def add_news_bulk(
    news_list: List[NewsCreate],
    db: Session = Depends(get_db)
) -> List[NewsRead]:
    return [create_news(db, item) for item in news_list]

# 5) CRUD: 저장된 뉴스 조회 (GET /news or /news/)
@router.get("", response_model=List[NewsRead])
@router.get("/", response_model=List[NewsRead])
async def read_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[NewsRead]:
    return get_news(db, skip, limit)

# 6) CRUD: 특정 뉴스 상세 조회 (GET /news/{news_id})
@router.get("/{news_id}", response_model=NewsRead)
async def read_news_detail(
    news_id: int,
    db: Session = Depends(get_db)
) -> NewsRead:
    news = get_news_by_id(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news

# 7) CRUD: 뉴스 삭제 (DELETE /news/{news_id})
@router.delete("/{news_id}")
async def remove_news(
    news_id: int,
    db: Session = Depends(get_db)
):
    success = delete_news(db, news_id)
    if not success:
        raise HTTPException(status_code=404, detail="News not found")
    return {"ok": True}