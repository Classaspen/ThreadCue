from __future__ import annotations

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from .models import Base


DEFAULT_DB_PATH = Path.home() / ".attention-inbox" / "attention.db"


def create_database(path: str | Path = DEFAULT_DB_PATH):
    database_path = Path(path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(engine)
    return engine


def session_factory(engine):
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
