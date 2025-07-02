from fastapi import FastAPI
from backend.app.db.models import init_db
from backend.app.routers.news import router as news_router
from backend.app.routers.predict_rout import router as predict_router

# Ariadne 관련 import
from ariadne.asgi import GraphQL
from backend.app.graphql.schema import graphql_schema
from backend.app.graphql.context import graphql_context

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    init_db()

# RESTful 라우터 등록
app.include_router(news_router)
app.include_router(predict_router)

# GraphQL 엔드포인트 등록 (POST & GET)
app.add_route("/graphql", GraphQL(schema=graphql_schema, context_value=graphql_context))
# Playground를 위한 GET
app.add_websocket_route("/graphql", GraphQL(schema=graphql_schema, context_value=graphql_context))