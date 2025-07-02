# tests/test_predict.py

import sys, os
# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

@pytest.mark.parametrize("payload, expected_entities", [
    ({"text": "삼성전자가 어제 코스피 시장에서 급등했다."}, ["삼성전자", "급등"]),
    ({"text": "애플이 오늘 주가가 하락했다."}, ["애플","하락"])
])
def test_predict_text_input(payload, expected_entities):
    # POST /predict 에 텍스트만 보내는 경우
    response = client.post("/predict", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    # 응답 포맷 검증
    assert "entities" in data
    assert "predictions" in data
    assert isinstance(data["entities"], list)
    assert isinstance(data["predictions"], list)

    # 엔티티 추출 결과에 최소 하나 이상의 기대값이 포함되어 있는지 확인
    extracted = [e["entity"] for e in data["entities"]]
    for ent in expected_entities:
        assert ent in extracted

def test_predict_news_id_input(monkeypatch):
    # DB 조회를 모킹해서 news_id 기반 호출 테스트
    dummy = type("News", (), {"title": "테스트", "description": "테스트 설명"})
    # get_news_by_id를 로컬 dummy로 대체
    from backend.app.services.crud import get_news_by_id
    monkeypatch.setattr("backend.app.routers.predict_rout.get_news_by_id", lambda db, nid: dummy)

    response = client.post("/predict", json={"news_id": 42})
    assert response.status_code == 200, response.text
    data = response.json()

    # mock된 dummy 텍스트가 사용됐는지 확인
    assert any(p["asset"] == "테스트" for p in data["predictions"])

def test_predict_input_validation_error():
    # news_id도, text도 없는 경우 422
    response = client.post("/predict", json={})
    assert response.status_code == 422
