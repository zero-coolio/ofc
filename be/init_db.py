# Initialize the SQLite database for OFC (FastAPI + SQLModel).
# Usage:
#   python init_db.py
# Creates tables and, if none exist, a bootstrap user with an API key.

import secrets
from sqlmodel import SQLModel, Session
from app.database import engine
from app.models import User, Category, Transaction  # register tables


def init_db():
    print("🚀 Initializing SQLite database ...")
    SQLModel.metadata.create_all(engine)
    print("✅ Tables created.")

    with Session(engine) as session:
        first_user = session.query(User).first()
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
