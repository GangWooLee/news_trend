# backend/app/routers/predict_rout.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, root_validator

from backend.app.services.ner import extract_entities
from backend.app.services.cot import cot_predict
from backend.app.db.session import get_db
from backend.app.services.crud import get_news_by_id

router = APIRouter(prefix="/predict", tags=["predict"])

class PredictRequest(BaseModel):
    news_id: Optional[int] = None
    text: Optional[str]    = None

    @root_validator
    def check_one_of(cls, values):
        nid, txt = values.get("news_id"), values.get("text")
        if not (nid or txt):
            raise ValueError("news_id or text is required")
        return values

class Entity(BaseModel):
    entity: str
    label: str

class Prediction(BaseModel):
    asset: str
    direction: str
    confidence: Optional[float]
    reasoning: str

class PredictResponse(BaseModel):
    entities: List[Entity]
    predictions: List[Prediction]

@router.post("/", response_model=PredictResponse)
async def predict(
    request: PredictRequest,
    db: Session = Depends(get_db)
):
    # 1. Get text (from DB if news_id provided)
    if request.news_id:
        news = get_news_by_id(db, request.news_id)
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        text = news.title + "\n" + news.description
    else:
        text = request.text  # 이미 검증되어 있음

    # 2. NER로 개체 추출
    entities = extract_entities(text)

   # 3. Chain-of-Thought 예측
    predictions = cot_predict(entities, text)
    # ─── news_id 모드일 때 override & 기본 예측 보장 ───
    if request.news_id is not None:
        # 1) 기존 prediction들의 asset 덮어쓰기
        for pred in predictions:
            pred["asset"] = news.title
        # 2) 엔티티가 하나도 없어서 predictions가 비어있다면,
        #    뉴스 제목만 갖는 기본 prediction을 하나 추가
        if not predictions:
            predictions.append({
                "asset": news.title,
                "direction": "",      # 기본값
                "confidence": None,
                "reasoning": ""
            })

    # 4. dict로 리턴하면 FastAPI가 response_model로 감싸줍니다
    return {
        "entities": entities,
        "predictions": predictions
    }
