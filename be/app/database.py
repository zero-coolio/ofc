from typing import Any, Generator

from sqlmodel import SQLModel, create_engine
from sqlmodel import Session as SqlSession
import os
from logging import getLogger

from sqlmodel import SQLModel, select

logger = getLogger(__name__)

DEFAULT_SQLITE_PATH = os.path.join(".", "data", "transactions.db")
DATABASE_URL = os.getenv(
    "DATABASE_URL", f"sqlite:///{os.getenv('SQLITE_PATH', DEFAULT_SQLITE_PATH)}"
)
if DATABASE_URL.startswith("sqlite:///"):
    db_file = DATABASE_URL.replace("sqlite:///", "", 1)
    os.makedirs(os.path.dirname(db_file) or ".", exist_ok=True)
print(f"📄 SQLite file: {os.path.abspath(DEFAULT_SQLITE_PATH)}")
print(f"<UNK>  DB URL: {db_file}")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def init_db():
    from app.models import Transaction, Category

    u = DATABASE_URL
    logger.warn(f"database: {u}")
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[SqlSession, Any, None]:
    with SqlSession(engine) as session:
        yield session
    # finally:
    #    session.close()


def open_session() -> SqlSession:
    return SqlSession(engine)
