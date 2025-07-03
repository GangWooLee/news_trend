# scripts/export_model.py

from transformers import AutoModelForSequenceClassification, AutoTokenizer
from pathlib import Path

MODEL_NAME = "EleutherAI/gpt-neo-125M"   # 혹은 fine-tuned 모델 허브 ID
SAVE_DIR = Path("models/fine_tuned/predict_model")

# 원격에서 모델·토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model     = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# 내보내기
tokenizer.save_pretrained(SAVE_DIR)
model.save_pretrained(SAVE_DIR)

print("✅ 모델과 토크나이저를 올바르게 저장했습니다.")
