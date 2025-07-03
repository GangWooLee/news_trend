import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ─── 전역 캐시 변수 ───
_model = None
_tokenizer = None

# ─── GPU가 가능하면 GPU, 아니면 CPU ───
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model():
    global _model, _tokenizer
    if _model is None:
        # 토크나이저·모델 로드 (경로는 실제 위치에 맞게 수정)
        _tokenizer = AutoTokenizer.from_pretrained("models/fine_tuned/predict_model")
        _model = AutoModelForSequenceClassification.from_pretrained(
            "models/fine_tuned/predict_model"
        ).to(device)  # ─── device로 이동 ───
        _model.eval()
    return (_tokenizer, _model)

def model_predict(tokenizer_model_pair, texts, assets=None):
    tokenizer, model = tokenizer_model_pair

    # ─── 단일 호출도, 배치 호출도 모두 지원 ───
    if isinstance(texts, str):
        texts = [texts]
        assets = [assets]

    # ─── assets가 없거나 길이가 다르면 기본값 채우기 ───
    if assets is None or len(assets) != len(texts):
        assets = [None] * len(texts)

    # 토큰화 후 device로 이동
    enc = tokenizer(texts, padding=True, truncation=True, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**enc)
        logits = outputs.logits
        preds = torch.argmax(logits, dim=-1).tolist()
        confidences = torch.softmax(logits, dim=-1).max(dim=-1).values.tolist()

    # 결과 조립
    results = []
    for asset, pred_idx, confidence in zip(assets, preds, confidences):
        direction = "up" if pred_idx == 1 else "down"
        results.append({
            "asset": asset,
            "direction": direction,
            "confidence": confidence,
            "reasoning": ""
        })
    return results
