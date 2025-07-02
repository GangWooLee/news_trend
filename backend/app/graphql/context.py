# backend/app/graphql/context.py
from backend.app.db.session import SessionLocal
from typing import Dict, Any

async def graphql_context(request) -> Dict[str, Any]:
    """
    GraphQL context creator for Ariadne, injecting a SQLAlchemy session.

    Returns a dict with 'db' key containing a new SessionLocal instance.
    Make sure to close the session after request if necessary.
    """
    db = SessionLocal()
    return {"db": db}
