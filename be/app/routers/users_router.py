from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import User
from app.schemas import UserCreate, UserRead
from app.security import get_current_user
from app.services import users_service as svc

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, session: Session = Depends(get_session)):
    # Bootstrap the first user when DB is empty.
    existing = session.exec(select(User)).all()
    if existing:
        raise HTTPException(status_code=403, detail="Users already exist. Use /users/create with a valid API key.")
    try:
        return svc.bootstrap_user(session, email=payload.email, name=payload.name)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/create", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_authenticated(payload: UserCreate, session: Session = Depends(get_session), _: User = Depends(get_current_user)):
    try:
        return svc.create_user_authenticated(session, email=payload.email, name=payload.name)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user
