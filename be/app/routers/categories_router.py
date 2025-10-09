from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.models import User
from app.schemas import CategoryCreate, CategoryRead
from app.security import get_current_user
from app.services import categories_service as svc

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        return svc.create_category(session, user_id=user.id, name=payload.name)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("", response_model=list[CategoryRead])
def list_categories(
    session: Session = Depends(get_session), user: User = Depends(get_current_user)
):
    return svc.list_categories(session, user_id=user.id)


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        svc.delete_category(session, user_id=user.id, category_id=category_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Category not found")
    return
