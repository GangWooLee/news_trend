from typing import List, Dict

def predict_directions(entities: List[Dict], text: str) -> List[Dict]:
    """
    추출된 개체에 대해 자산 방향성을 예측합니다.
    실서비스에서는 ML/DL 모델 사용.
    """
    predictions = []
    for ent in entities:
        predictions.append({
            "asset": ent["entity"],
            "direction": "up" if "상승" in text else "neutral",
            "confidence": 0.5,
            "reasoning": f"텍스트에 '상승' 키워드 포함 여부에 따라 판단"
        })
    return predictions

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

# 1) 토크나이저 및 모델 초기화
test_model_name = 'EleutherAI/gpt-neo-125M'
real_model_name = "EleutherAI/gpt-j-6B"
MODEL_NAME = test_model_name
CACHE_DIR = "~/.cache/huggingface/transformers"
CACHE_DIR = os.path.expanduser(CACHE_DIR)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir = CACHE_DIR, local_files_only=False)
model     = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    cache_dir=CACHE_DIR,
    torch_dtype=torch.float16,
    local_files_only=False
)

# 2) 디바이스 설정 (GPU/CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# 3) 예시 함수

def load_model():
    """토크나이저와 모델 객체를 반환합니다."""
    return tokenizer, model, device

print(load_model())