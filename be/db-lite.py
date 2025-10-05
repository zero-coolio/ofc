"""
Initialize the SQLite database for the OFC (Open Finance Controller) app.
Run this once before starting the FastAPI server.
"""

from sqlmodel import SQLModel
from app.database import engine
from app.models import User, Category, Transaction


def init_db():
    print("🚀 Initializing SQLite database ...")
    SQLModel.metadata.create_all(engine)
    print("✅ Database tables created successfully.")


if __name__ == "__main__":
    init_db()
