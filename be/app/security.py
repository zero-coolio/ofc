from fastapi import Header, HTTPException, status, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import User

async def get_current_user(x_api_key: str | None = Header(default=None), session: Session = Depends(get_session)) -> User:
    total_users = session.exec(select(User)).all()
    if not total_users:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No users exist. Create one via POST /users to bootstrap.")
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key")
    user = session.exec(select(User).where(User.api_key == x_api_key)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return user
