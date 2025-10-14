
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from sqlmodel import Session
from ..database import get_session
from ..schemas import CategoryCreate, CategoryRead
from ..services import get_category_service, CategoryService
import logging
logger = logging.getLogger("ofc.routers.categories")

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=List[CategoryRead])
def list_categories(q: Optional[str]=Query(None, description="starts-with filter"), session: Session = Depends(get_session), svc: CategoryService = Depends(get_category_service)):
    logger.info("➡️  list_categories called q=%s", q)
    items = svc.list(q)
    logger.info("✅  list_categories count=%s", len(items))
    return [CategoryRead(**c.model_dump()) for c in items]

@router.post("", response_model=CategoryRead, status_code=201)
def create_category(payload: CategoryCreate, session: Session = Depends(get_session), svc: CategoryService = Depends(get_category_service)):
    logger.info("➡️  create_category called payload=%s", payload.model_dump())
    c = svc.create(payload)
    logger.info("✅  create_category created id=%s name=%s", c.id, c.name)
    return CategoryRead(**c.model_dump())
