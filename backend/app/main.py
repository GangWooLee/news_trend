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

from fastapi import FastAPI
from backend.app.db.models import init_db
from backend.app.routers.news import router as news_router
from backend.app.routers.predict_rout import router as predict_router

# Ariadne GraphQL imports
from ariadne.asgi import GraphQL
from backend.app.graphql.schema import graphql_schema
from backend.app.graphql.context import graphql_context

# ─── 모델 로드용 서비스 임포트 ───
from backend.app.services.model import load_model

# FastAPI 앱 생성
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    # DB 초기화
    init_db()
    # ─── Startup 시 모델을 한 번만 로드해 app.state에 저장 ───
    app.state.predict_model = load_model()

# RESTful 라우터 등록
app.include_router(news_router)
app.include_router(predict_router)

# GraphQL 엔드포인트 등록 (POST & GET)
app.add_route("/graphql", GraphQL(schema=graphql_schema, context_value=graphql_context))
app.add_websocket_route("/graphql", GraphQL(schema=graphql_schema, context_value=graphql_context))
