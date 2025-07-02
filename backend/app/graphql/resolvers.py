from typing import Any, Dict, List
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.services.scraper import fetch_news
from backend.app.services.crud import get_news, get_news_by_id
from backend.app.services.ner import extract_entities
from backend.app.services.predict_ser import predict_directions

# 각 Query 필드에 매핑할 함수

def resolve_search_news(obj: Any, info: Any, query: str, display: int = 10, start: int = 1, sort: str = "date") -> List[Dict]:
    return fetch_news(query=query, display=display, start=start, sort=sort)


def resolve_get_news(obj: Any, info: Any, skip: int = 0, limit: int = 100) -> List[Dict]:
    db: Session = info.context["db"]
    return get_news(db, skip, limit)


def resolve_predict(obj: Any, info: Any, newsId: int = None, text: str = None) -> Dict:
    
    db: Session = info.context["db"]
    if newsId:
        news = get_news_by_id(db, newsId)
        text = news.title + "\n" + news.description
    entities = extract_entities(text)
    predictions = predict_directions(entities, text)
    return {"entities": entities, "predictions": predictions}

# 필드명과 resolver 함수 매핑
resolvers_map = {
    "searchNews": resolve_search_news,
    "getNews": resolve_get_news,
    "predict": resolve_predict,
}