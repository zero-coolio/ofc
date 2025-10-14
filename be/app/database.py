from typing import Any, Generator

from sqlmodel import SQLModel, create_engine
from sqlmodel import Session as SqlSession
import os

DEFAULT_SQLITE_PATH = os.path.join(".", "data", "transactions.db")
DATABASE_URL = os.getenv(
    "DATABASE_URL", f"sqlite:///{os.getenv('SQLITE_PATH', DEFAULT_SQLITE_PATH)}"
)
if DATABASE_URL.startswith("sqlite:///"):
    db_file = DATABASE_URL.replace("sqlite:///", "", 1)
    os.makedirs(os.path.dirname(db_file) or ".", exist_ok=True)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[SqlSession, Any, None]:
    with SqlSession(engine) as session:
        yield session
    # finally:
    #    session.close()


def open_session() -> SqlSession:
    return SqlSession(engine)
