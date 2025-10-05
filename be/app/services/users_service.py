import secrets
from sqlmodel import Session
from app.data.repositories import UserRepo

def bootstrap_user(session: Session, *, email: str, name: str | None):
    repo = UserRepo(session)
    if repo.get_by_email(email):
        raise ValueError("Email already registered")
    api_key = secrets.token_hex(16)
    user = repo.create(email=email, name=name, api_key=api_key)
    return user

def create_user_authenticated(session: Session, *, email: str, name: str | None):
    repo = UserRepo(session)
    if repo.get_by_email(email):
        raise ValueError("Email already registered")
    api_key = secrets.token_hex(16)
    user = repo.create(email=email, name=name, api_key=api_key)
    return user
