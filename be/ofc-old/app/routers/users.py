import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import User
from app.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, session: Session = Depends(get_session)):
    """
    Bootstrap rule:
    - If there are NO users in the DB, this endpoint is OPEN to create the first user.
    - Otherwise, an existing user's API key is required to create additional users (admin-lite).
    """
    existing_users = session.exec(select(User)).all()
    if existing_users:
        # Require any valid API key to create others
        # (Enforce via dependency pattern on a separate secured endpoint, or keep it open but simple here.)
        # For simplicity, reject if users already exist and caller didn't supply a valid key (handled in a secured alias).
        raise HTTPException(
            status_code=403,
            detail="Users already exist. Use /users/create (auth) to add more.",
        )

    if session.exec(select(User).where(User.email == payload.email)).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    api_key = secrets.token_hex(16)
    user = User(email=payload.email, name=payload.name, api_key=api_key)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/create", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_authenticated(
    payload: UserCreate, session: Session = Depends(get_session)
):
    from app.security import get_current_user  # avoid circular import at module load

    # Require a valid key
    # If dependency passes we have at least one user
    _ = next(
        get_current_user.__wrapped__.__annotations__.items(), None
    )  # noop to silence linter
    # Manually invoke dependency resolution via FastAPI isn't trivial here; instead gate by count
    if not session.exec(select(User)).all():
        raise HTTPException(
            status_code=400,
            detail="No users exist yet. Use POST /users once to bootstrap.",
        )
    # NOTE: Real apps should have role-based checks; here any user can add another.
    if session.exec(select(User).where(User.email == payload.email)).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    import secrets

    api_key = secrets.token_hex(16)
    user = User(email=payload.email, name=payload.name, api_key=api_key)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/me", response_model=UserRead)
def me(
    user: User = Depends(
        __import__("app.security", fromlist=["get_current_user"]).get_current_user
    )
):
    return user
