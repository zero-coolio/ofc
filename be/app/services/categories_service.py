from sqlmodel import Session
from app.data.repositories import CategoryRepo
from app.models import Category

def create_category(session: Session, *, user_id: int, name: str) -> Category:
    repo = CategoryRepo(session)
    if repo.get_by_name_for_user(user_id, name):
        raise ValueError("Category with that name already exists")
    return repo.create(user_id=user_id, name=name)

def list_categories(session: Session, *, user_id: int):
    return CategoryRepo(session).list_for_user(user_id)

def delete_category(session: Session, *, user_id: int, category_id: int):
    repo = CategoryRepo(session)
    cat = repo.get_by_id(category_id)
    if not cat or cat.user_id != user_id:
        raise LookupError("Category not found")
    repo.delete(cat)
