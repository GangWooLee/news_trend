# backend/app/services/cot.py
from typing import List, Dict, Tuple
from backend.app.services.predict_ser import load_model
import torch

# 모델과 토크나이저 로드
tokenizer, model, device = load_model()

# CoT(Chain-of-Thought) 프롬프트 생성 함수
def generate_cot_prompt(entity: str, text: str) -> str:
    """
    주어진 뉴스 텍스트와 자산명에 대해 단계별 사고 과정을 요청하는 CoT 프롬프트를 생성합니다.
    """
    prompt = (
        f"뉴스 기사:\n{text}\n"
        f"분석 대상 자산: {entity}\n"
        "위 자산의 가격 방향성을 'up', 'down', 'neutral' 중 하나로 예측하세요.\n"
        "또한, 예측 근거를 단계별로 서술해주세요.\n"
        "단계별 사고 과정:\n"
    )
    return prompt

# CoT 결과에서 사고 과정(reasoning)과 최종 예측(direction)을 파싱
def parse_cot_output(decoded: str, prompt: str) -> Tuple[str, str]:
    """
    디코딩된 모델 출력을 받아, 사고 과정과 결과를 분리하여 반환합니다.
    """
    # 프롬프트 부분 제거
    body = decoded[len(prompt):]
    # '결과:' 또는 'Result:' 키워드 기준 분리
    sep = '결과:' if '결과:' in body else 'Result:'
    if sep in body:
        parts = body.split(sep, 1)
        reasoning = parts[0].strip()
        direction = parts[1].split()[0].strip()
    else:
        # 키워드가 없으면 전체를 사고 과정으로 처리
        reasoning = body.strip()
        direction = ''
    return reasoning, direction

# CoT 기반 예측 함수
def cot_predict(entities: List[Dict], text: str, max_new_tokens: int = 100) -> List[Dict]:
    """
    뉴스 텍스트에서 추출된 개체명 리스트에 대해 CoT 방식을 사용해 방향성을 예측합니다.

    Returns:
        List of {'asset': str, 'direction': str, 'confidence': float, 'reasoning': str}
    """
    results: List[Dict] = []
    for ent in entities:
        prompt = generate_cot_prompt(ent['entity'], text)
        inputs = tokenizer(prompt, return_tensors='pt').to(device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            eos_token_id=tokenizer.eos_token_id,
        )
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        reasoning, direction = parse_cot_output(decoded, prompt)
        results.append({
            'asset': ent['entity'],
            'direction': direction,
            'confidence': None,  # 필요시 추후 confidence 산출
            'reasoning': reasoning
        })
    return results
