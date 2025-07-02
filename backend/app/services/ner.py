# # backend/app/services/ner.py
# import spacy
# from typing import List, Dict
# from .filter_helpers import filter_entities

# # 한국어 NER 모델 로딩 (한 번만 수행)
# nlp = spacy.load("ko_core_news_sm")

# # 제거할 라벨
# UNNEEDED_LABELS = {"DT", "TIME", "DATE"}

# def extract_entities(text: str) -> List[Dict]:
#     """
#     spaCy 한국어 모델을 사용해 텍스트에서 개체명(Entity)을 추출합니다.

#     Parameters
#     ----------
#     text : str
#         분석할 뉴스 텍스트

#     Returns
#     -------
#     List[Dict]
#         각 개체명에 대해 `{'entity': str, 'label': str}` 형태의 리스트
#     """
#     doc = nlp(text)
#     entities: List[Dict] = []
#     for ent in doc.ents:
#         # 조사 제거
#         ent_text = ent.text
#         if ent_text.endswith(("이", "가")):
#             ent_text = ent_text[:-1]
#         entities.append({"entity": ent_text, "label": ent.label_})
#     # 필요 없는 라벨(ZT, TIME 등) 제거
#     return [e for e in entities if e["label"] not in UNNEEDED_LABELS]
# backend/app/services/ner.py

# from typing import List, Dict

# # 제거할 불필요 토큰
# STOPWORDS = {"어제", "오늘", "어제도", "오늘도"}

# def extract_entities(text: str) -> List[Dict]:
#     """
#     아주 단순하게, 공백으로 나뉜 덩어리들을 모두 엔티티로 취급합니다.
#     STOPWORDS에 포함된 날짜/시간 표현만 걸러냅니다.
#     """
#     # 구두점(.) 제거, 개행·탭을 공백으로
#     clean = text.replace("\n", " ").replace("\t", " ").replace(".", "")
#     tokens = clean.split()
#     entities: List[Dict] = []
#     for tok in tokens:
#         if tok in STOPWORDS:
#             continue
#         # 최소 두 글자 이상인 것만
#         if len(tok) > 1:
#             entities.append({"entity": tok, "label": ""})
#     return entities

# backend/app/services/ner.py
import spacy
from typing import List, Dict

# load the Korean model once
nlp = spacy.load("ko_core_news_sm")

# only these labels are actual assets we care about
ALLOWED_LABELS = {"OG", "LC"}

# common single- and double-character Korean josa
JOSA_LIST = ["으로", "로", "이", "가", "을", "를", "은", "는", "도", "와", "과"]

def extract_entities(text: str) -> List[Dict]:
    """
    spaCy 한국어 모델을 사용해 텍스트에서 자산 개체명(Entity)을 추출합니다.
    OG(기관), LC(지수) 라벨만 남기고, 
    끝에 조사가 붙은 경우 조사를 제거한 엔트리도 함께 리턴합니다.
    """
    doc = nlp(text)
    entities: List[Dict] = []

    # 1) keep only allowed labels
    for ent in doc.ents:
        if ent.label_ in ALLOWED_LABELS:
            entities.append({"entity": ent.text, "label": ent.label_})

    # 2) for each, also add a josa-stripped variant
    final_entities: List[Dict] = []
    for ent in entities:
        text0 = ent["entity"]
        final_entities.append(ent)
        for j in JOSA_LIST:
            if text0.endswith(j):
                stripped = text0[:-len(j)]
                if stripped:
                    final_entities.append({"entity": stripped, "label": ent["label"]})
                break
    MOVEMENT_KEYWORDS = ["급등", "하락"]
    for kw in MOVEMENT_KEYWORDS:
        if kw in text and not any(e["entity"] == kw for e in final_entities):
            final_entities.append({"entity": kw, "label": "PRICE_MOVE"}) 
    return final_entities
