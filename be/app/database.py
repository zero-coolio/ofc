from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine, Session
import os
from typing import Optional

DATABASE_URL = os.getenv("OFC_DATABASE_URL", "sqlite:///./ofc")  # .db

eng: Optional[Engine] = None


def get_engine(suffix: str = ".db"):
    if suffix:
        url = DATABASE_URL + suffix
    global eng
    if not eng:
        eng = create_engine(
            url,
            connect_args=(
                {"check_same_thread": False} if url.startswith("sqlite") else {}
            ),
        )
    return eng


def init_db(suffix: str = None) -> Engine:
    eng = get_engine(suffix)
    SQLModel.metadata.create_all(eng)
    return eng


def get_session():
    with Session(eng) as session:
        yield session
