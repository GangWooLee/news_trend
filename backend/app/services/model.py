# backend/app/services/model.py

import torch
from pathlib import Path
from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    PreTrainedTokenizerFast
)

_model = None
_tokenizer = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model():
    global _model, _tokenizer
    if _model is None:
        # 1) 로컬 모델 폴더 경로 계산
        project_root = Path(__file__).resolve().parents[3]
        model_dir = project_root / "models" / "fine_tuned" / "predict_model"
        if not model_dir.exists():
            raise RuntimeError(f"모델 폴더가 없습니다: {model_dir}")

        # 2) Config 로드
        #    로컬 config.json이 깨져 있을 수 있으니, 허브에서 기본 config를 가져오도록 합니다.
        try:
            config = AutoConfig.from_pretrained(
                str(model_dir),
                local_files_only=True
            )
        except Exception:
            # 로컬 로드 실패 시 허브에서 기본 모델의 Config 사용
            config = AutoConfig.from_pretrained("EleutherAI/gpt-neo-125M")


        # 3) 모델 인스턴스 생성 & 가중치 로드
        model = AutoModelForSequenceClassification.from_config(config).to(device)
        state_dict = torch.load(model_dir / "pytorch_model.bin", map_location=device)
        model.load_state_dict(state_dict)
        model.eval()

        # 4) 토크나이저 직접 로드 (json 파일을 지정)
        tokenizer = PreTrainedTokenizerFast(
            tokenizer_file=str(model_dir / "tokenizer.json")
        )

        _model = model
        _tokenizer = tokenizer

    return (_tokenizer, _model)

def model_predict(tokenizer_model_pair, texts, assets=None):
    tokenizer, model = tokenizer_model_pair

    if isinstance(texts, str):
        texts, assets = [texts], [assets]
    if assets is None or len(assets) != len(texts):
        assets = [None] * len(texts)

    # 토크나이즈
    enc = tokenizer(
        texts,
        padding=True,
        truncation=True,
        return_tensors="pt"
    )
    # 장치로 이동
    for k, v in enc.items():
        enc[k] = v.to(device)

    with torch.no_grad():
        outputs = model(**enc)
        logits = outputs.logits

    preds = torch.argmax(logits, dim=-1).tolist()
    confs = torch.softmax(logits, dim=-1).max(dim=-1).values.tolist()

    results = []
    for asset, pred_idx, conf in zip(assets, preds, confs):
        direction = "up" if pred_idx == 1 else "down"
        results.append({
            "asset": asset,
            "direction": direction,
            "confidence": conf,
            "reasoning": ""
        })
    return results
