# Initialize the SQLite database for OFC (FastAPI + SQLModel).
# Usage:
#   python init_db.py
# Creates tables and, if none exist, a bootstrap user with an API key.

import secrets
from sqlmodel import SQLModel, Session
from app.database import get_engine
from app.models import User, Category, Transaction  # register tables
from sqlmodel import select


def init_db():
    eng = get_engine()
    print("🚀 Initializing SQLite database ...", eng.url)

    SQLModel.metadata.create_all(eng)
    print("✅ Tables created.")

    with Session(eng) as session:
        first_user = session.exec(select(User)).first()
        if not first_user:
            api_key = secrets.token_hex(16)
            user = User(email="admin@example.com", name="Admin", api_key=api_key)
            session.add(user)
            session.commit()
            print("✅ Created bootstrap user:", user.email)
            print("🔑 API Key:", api_key)
        else:
            print("ℹ️ Users already exist — skipping bootstrap user.")


if __name__ == "__main__":
    init_db()
    print("✅ Init db", get_engine().url)
