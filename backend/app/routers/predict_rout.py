# backend/app/routers/predict_rout.py

from fastapi import APIRouter, HTTPException, Request, Depends
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

def get_request(request: Request):
    return request

async def _predict_one(payload: PredictRequest, db: Session, request: Request):
    # 1) 텍스트 결정
    if payload.news_id is not None:
        news = get_news_by_id(db, payload.news_id)
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        text = f"{news.title}\n{news.description}"
        asset_name = news.title
    else:
        text = request.text
        asset_name = None

    # 2) 엔티티 추출
    entities = extract_entities(text)

    # 3) Chain-of-Thought 예측
    #    (또는 model_predict 함수 사용 가능)
    predictions = cot_predict(entities, text)

    # ─── news_id 모드면 asset 덮어쓰기 및 기본 예측 보장 ───
    if asset_name is not None:
        for p in predictions:
            p["asset"] = asset_name
        if not predictions:
            predictions.append({
                "asset": asset_name,
                "direction": "",
                "confidence": None,
                "reasoning": ""
            })

    return {"entities": entities, "predictions": predictions}

@router.post("/", response_model=PredictResponse)
async def predict(
    payload: PredictRequest,
    db: Session = Depends(get_db),
    request: Request = Depends(get_request)
):
    # 시작 시 로드된 모델 확인용(필요시 model_predict 호출)
    _ = request.app.state.predict_model
    return await _predict_one(payload, db, request)

@router.post("/batch", response_model=List[PredictResponse])
async def predict_batch(
    items: List[PredictRequest],
    db: Session = Depends(get_db),
    request: Request = Depends(get_request)
):
    results = []
    for item in items:
        res = await _predict_one(item, db, request)
        results.append(res)
    return results
