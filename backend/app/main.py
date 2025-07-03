# from fastapi import FastAPI
# from backend.app.db.models import init_db
# from backend.app.routers.news import router as news_router
# from backend.app.routers.predict_rout import router as predict_router

# # Ariadne 관련 import
# from ariadne.asgi import GraphQL
# from backend.app.graphql.schema import graphql_schema
# from backend.app.graphql.context import graphql_context

# app = FastAPI()

# @app.on_event("startup")
# async def on_startup():
#     init_db()

# # RESTful 라우터 등록
# app.include_router(news_router)
# app.include_router(predict_router)

# # GraphQL 엔드포인트 등록 (POST & GET)
# app.add_route("/graphql", GraphQL(schema=graphql_schema, context_value=graphql_context))
# # Playground를 위한 GET
# app.add_websocket_route("/graphql", GraphQL(schema=graphql_schema, context_value=graphql_context))

# backend/app/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager

from backend.app.db.models import init_db
from backend.app.routers.news import router as news_router
from backend.app.routers.predict_rout import router as predict_router

# Ariadne GraphQL imports
from ariadne.asgi import GraphQL
from backend.app.graphql.schema import graphql_schema
from backend.app.graphql.context import graphql_context

# ─── 모델 로드용 서비스 임포트 ───
from backend.app.services.model import load_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1) 애플리케이션 시작 시 실행
    init_db()                                # DB 초기화
    app.state.predict_model = load_model()   # 모델 로드 및 캐싱
    yield
    # 2) 애플리케이션 종료 시 실행 (필요 시 정리 로직 추가)
    # 예: await some_cleanup()

# FastAPI 인스턴스 생성 시 lifespan 전달
app = FastAPI(lifespan=lifespan)

# RESTful 라우터 등록
app.include_router(news_router)
app.include_router(predict_router)

# GraphQL 엔드포인트 등록 (POST & GET)
app.add_route(
    "/graphql",
    GraphQL(schema=graphql_schema, context_value=graphql_context)
)
app.add_websocket_route(
    "/graphql",
    GraphQL(schema=graphql_schema, context_value=graphql_context)
)
