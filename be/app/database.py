import os
from typing import Iterator
from sqlmodel import SQLModel, create_engine, Session, Engine

_DATABASE_URL = os.getenv("OFC_DATABASE_URL", "sqlite:///./ofc.db")
_engine: Engine | None = None

def get_engine() -> Engine:
    global _engine
    if _engine is None:
        connect_args = {"check_same_thread": False} if _DATABASE_URL.startswith("sqlite") else {}
        _engine = create_engine(_DATABASE_URL, connect_args=connect_args)
    return _engine

def init_db() -> None:
    SQLModel.metadata.create_all(get_engine())

def get_session() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session
