from typing import Optional
from sqlmodel import Session
from ..models import Category
from ..schemas import CategoryCreate
from ..storage.categories_repo import CategoryRepository
import logging

log = logging.getLogger("ofc.services.categories")


class CategoryService:
    def __init__(self, session: Session):
        self.repo = CategoryRepository(session)

    def list(self, q: Optional[str] = None):
        log.info("🧩 Service: list categories q=%s", q)
        return self.repo.list(starts_with=q)

    def create_if_missing(self, name: str) -> Category:
        name = name.strip()
        if not name:
            raise ValueError("Category name required")
        found = self.repo.get_by_name(name)
        if found:
            log.info("🧩 Service: category exists name=%s id=%s", name, found.id)
            return found
        created = self.repo.add(Category(name=name))
        log.info("🧩 Service: category created id=%s name=%s", created.id, created.name)
        return created

    def create(self, payload: CategoryCreate) -> Category:
        return self.create_if_missing(payload.name)
