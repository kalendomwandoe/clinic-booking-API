import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Falls back to a local SQLite file if DATABASE_URL isn't set — this only matters for environments like CI that never actually use `engine` (testsoverride get_db with their own in-memory SQLite session), so this exists purely to prevent create_engine() crashing at import time.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fallback_unused.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()