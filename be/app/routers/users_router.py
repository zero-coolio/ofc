from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import User
from app.schemas import UserCreate, UserRead
from app.security import get_current_user
from app.services import users_service as svc
from fastapi import Query, Depends

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, session: Session = Depends(get_session)):
    # Bootstrap the first user when DB is empty.
    sel = select(User)
    r = session.exec(sel)
    existing = r.all()
    if existing:
        raise HTTPException(
            status_code=403,
            detail="Users already exist. Use /users/create with a valid API key.",
        )
    try:
        return svc.bootstrap_user(session, email=payload.email, name=payload.name)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/create", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_authenticated(
    payload: UserCreate,
    session: Session = Depends(get_session),
    email: str = Query(default=None),
    name: str = Query(default=None),
):
    try:
        if not email:
            payload["email"] = email
        if not name:
            payload["name"] = name
        u = svc.create_user_authenticated(
            session, email=payload.email, name=payload.name
        )
        return u
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


# convience method for testing/debugging from browser
@router.get(
    "/create/{name}/{email}",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    session: Session = Depends(get_session), email: str = None, name: str = None
):
    try:
        u = svc.create_user_authenticated(session, email=email, name=name)
        return u
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user
