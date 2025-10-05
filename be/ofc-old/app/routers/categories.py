from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session

from app.database import get_session
from app.models import Category, User
from app.schemas import CategoryCreate, CategoryRead
from app.security import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    existing = session.exec(
        select(Category).where(
            Category.user_id == user.id, Category.name == payload.name
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=409, detail="Category with that name already exists"
        )
    cat = Category(name=payload.name, user_id=user.id)
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat


@router.get("", response_model=list[CategoryRead])
def list_categories(
    session: Session = Depends(get_session), user: User = Depends(get_current_user)
):
    return session.exec(
        select(Category).where(Category.user_id == user.id).order_by(Category.name)
    ).all()


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    cat = session.get(Category, category_id)
    if not cat or cat.user_id != user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(cat)
    session.commit()
    return
