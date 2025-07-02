# setup.py
from setuptools import setup, find_packages

setup(
    name="news-asset-predictor",
    version="0.1.0",
    # backend 디렉토리 아래의 모든 패키지를 찾아서 설치
    packages=find_packages(include=["backend", "backend.*"]),
    package_dir={"backend": "backend"},
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "pydantic-settings",
        "requests",
        "feedparser",
        "SQLAlchemy",
        "graphene",
        # graphene-fastapi 는 PyPI에 없으니 빼거나 대체 패키지 사용
        "transformers",
        "torch",
        "spacy"
    ],
)
