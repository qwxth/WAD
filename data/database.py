from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data.models import Base

# Используем psycopg (версия 3, чистый Python)
DATABASE_URL = "postgresql+psycopg://loadforecast:loadforecast123@localhost:5432/loadforecast_db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
