from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings

engine = create_engine(settings.DB_URL, connect_args={"check_same_thread": False})  # SQLite 사용 시
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()