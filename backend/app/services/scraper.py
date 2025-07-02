import requests
import feedparser
from typing import List, Dict
from datetime import datetime
from backend.app.config import settings

BASE_URL = "https://openapi.naver.com/v1/search/news.json"

# 네이버 뉴스 검색 API

def fetch_news(
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = "date"
) -> List[Dict]:
    headers = {
        "X-Naver-Client-Id":     settings.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": display, "start": start, "sort": sort}
    resp = requests.get(BASE_URL, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json().get("items", [])

# 전체 뉴스 RSS 파싱

def fetch_news_by_rss(
    max_articles: int = 10
) -> List[Dict]:
    rss_url = (
        "https://news.naver.com/main/main.naver"
        "?mode=LSD&mid=shm&sid1=0&type=RSS"
    )
    resp = requests.get(rss_url)
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)

    articles: List[Dict] = []
    for entry in feed.entries[:max_articles]:
        articles.append({
            "title":        entry.title,
            "link":         entry.link,
            "originallink": entry.link,
            "description":  getattr(entry, "summary", ""),
            "pubDate":      getattr(entry, "published", datetime.now().isoformat()),
        })
    return articles