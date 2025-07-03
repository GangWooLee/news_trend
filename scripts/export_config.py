# scripts/export_config.py

from transformers import AutoConfig
from pathlib import Path

# 1) 사용할 베이스 모델 이름
BASE_MODEL = "EleutherAI/gpt-neo-125M"
# 2) 내보낼 디렉터리 (기존 predict_model 경로)
TARGET_DIR = Path("models/fine_tuned/predict_model")

if not TARGET_DIR.exists():
    raise RuntimeError(f"{TARGET_DIR} 폴더가 없습니다.")

# 3) Config 로드 & 저장
config = AutoConfig.from_pretrained(BASE_MODEL)
config.save_pretrained(str(TARGET_DIR))

print(f"✅ {BASE_MODEL} 의 config.json 을 {TARGET_DIR} 에 재생성했습니다.")
