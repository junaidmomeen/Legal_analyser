import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_db_url() -> str | None:
    return os.getenv("DATABASE_URL")


engine = create_engine(get_db_url()) if get_db_url() else None
SessionLocal = sessionmaker(bind=engine) if engine else None


