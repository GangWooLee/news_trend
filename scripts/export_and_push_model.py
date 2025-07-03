#!/usr/bin/env python3
# scripts/export_and_push_model.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pathlib import Path

# 1) 로컬에 이미 있는 모델/토크나이저 디렉터리가 있다면 생략하고,
#    없으면 허브에서 받아서 저장해 두기
BASE_MODEL = "EleutherAI/gpt-neo-125M"  
HUB_REPO   = "kbmbrs/news_trend"  # 업로드할 허브 리포 이름

# 로컬 저장소 경로 (옵션)
LOCAL_DIR = Path("models/fine_tuned/predict_model")

# 2) 모델·토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
model     = AutoModelForSequenceClassification.from_pretrained(BASE_MODEL)

# 3) 허브에 푸시
print(f"Pushing tokenizer to hub repo {HUB_REPO}...")
tokenizer.push_to_hub(HUB_REPO)

print(f"Pushing model to hub repo {HUB_REPO}...")
model.push_to_hub(HUB_REPO)

print("✅ Done!")
