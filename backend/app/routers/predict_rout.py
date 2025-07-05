# backend/app/routers/predict_rout.py

from fastapi import APIRouter, HTTPException, Depends  # FastAPI 라우터 및 예외, 의존성
from sqlalchemy.orm import Session                        # DB 세션 타입
from typing import List, Optional                         # 타입 힌팅
from pydantic import BaseModel, root_validator           # 요청/응답 모델 검증

# 서비스 로직 임포트
from backend.app.services.ner import extract_entities    # NER(개체명 인식) 추출 함수
from backend.app.services.cot import cot_predict          # Chain-of-Thought 예측 함수
from backend.app.db.session import get_db                # DB 세션 종속성
from backend.app.services.crud import get_news_by_id     # 뉴스 조회 함수

# 라우터 생성: /predict 경로로 시작하는 모든 엔드포인트에 적용
router = APIRouter(prefix="/predict", tags=["predict"])

# 요청 바디 스키마 정의: news_id 또는 text 중 하나는 필수
class PredictRequest(BaseModel):
    news_id: Optional[int] = None  # 뉴스 ID (DB 조회용)
    text: Optional[str]    = None  # 직접 입력한 텍스트

    @root_validator
    def check_one_of(cls, values):
        # 둘 다 없으면 에러 발생
        nid, txt = values.get("news_id"), values.get("text")
        if not (nid or txt):
            raise ValueError("news_id or text is required")
        return values

# 응답에 포함될 엔티티 모델
class Entity(BaseModel):
    entity: str  # 추출된 개체명 문자열
    label: str   # 개체 유형(label)

# 응답에 포함될 예측 결과 모델
class Prediction(BaseModel):
    asset: str                # 예측 대상 자산 이름
    direction: str            # up/down 예측
    confidence: Optional[float]  # 예측 확신도(0~1)
    reasoning: str            # 예측 근거 설명

# 최종 응답 스키마: 엔티티 리스트 + 예측 리스트
class PredictResponse(BaseModel):
    entities: List[Entity]
    predictions: List[Prediction]

# 내부 헬퍼 함수: 단일 요청 처리 로직
async def _predict_one(payload: PredictRequest, db: Session):
    # 1) 텍스트 결정: news_id 모드 vs text 직접 모드
    if payload.news_id is not None:
        # DB에서 뉴스 조회
        news = get_news_by_id(db, payload.news_id)
        if not news:
            # 없는 ID면 404 에러
            raise HTTPException(status_code=404, detail="News not found")
        # title + description 합쳐서 사용
        text = f"{news.title}\n{news.description}"
        asset_name = news.title
    else:
        # 직접 입력된 텍스트 사용
        text = payload.text
        asset_name = None

    # 2) NER로 엔티티 추출
    entities = extract_entities(text)

    # 3) Chain-of-Thought 방식으로 예측 수행
    predictions = cot_predict(entities, text)

    # 4) news_id 모드일 땐 asset명 덮어쓰기, 결과 없으면 기본값 추가
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

    # 최종 결과 딕셔너리 반환
    return {"entities": entities, "predictions": predictions}

# 단일 예측 엔드포인트
@router.post("/", response_model=PredictResponse)
async def predict(
    payload: PredictRequest,                   # 요청 본문 파싱
    db: Session = Depends(get_db)              # DB 세션 주입
):
    return await _predict_one(payload, db)     # 헬퍼 호출

# 배치 예측 엔드포인트
@router.post("/batch", response_model=List[PredictResponse])
async def predict_batch(
    payloads: List[PredictRequest],            # 요청 본문으로 여러 PredictRequest 배열 받음
    db: Session = Depends(get_db)              # DB 세션 주입
):
    results = []                               # 결과 리스트
    for p in payloads:
        res = await _predict_one(p, db)        # 각 요청별 예측 수행
        results.append(res)
    return results                             # 전체 결과 반환
