# backend/app/services/filter_helpers.py

from typing import List, Dict

# 필터링 가능한 불필요 라벨 정의
UNNEEDED_LABELS = {"DT", "TIME", "DATE"}


def filter_entities(entities: List[Dict]) -> List[Dict]:
    """
    NER 후, 불필요한 라벨(DT, TIME, DATE 등)을 제거합니다.
    """
    return [ent for ent in entities if ent.get("label") not in UNNEEDED_LABELS]
