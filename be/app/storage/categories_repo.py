
from typing import Optional, List
from sqlmodel import Session, select
from .base import BaseRepository
from ..models import Category

class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: Session):
        super().__init__(session, Category)

    def get_by_name(self, name: str) -> Optional[Category]:
        return self.session.exec(select(Category).where(Category.name == name)).first()

    def list(self, starts_with: Optional[str] = None) -> List[Category]:
        q = select(Category)
        if starts_with:
            q = q.where(Category.name.ilike(f"{starts_with}%"))
        q = q.order_by(Category.name.asc())
        return self.session.exec(q).all()
