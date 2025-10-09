import secrets
from sqlmodel import SQLModel, Session, select
from app.database import get_engine
from app.models import User


def init_db():
    print("🚀 Initializing SQLite database ...")
    SQLModel.metadata.create_all(get_engine())
    print("✅ Tables created.")

    with Session(get_engine()) as session:
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
