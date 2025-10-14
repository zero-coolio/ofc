from .transactions_service import TransactionService
from .categories_service import CategoryService
from .stats_service import StatsService

from app.database import get_session
from sqlmodel import Session
from fastapi import FastAPI, Depends


def get_transaction_service(session: Session = Depends(get_session)) -> TransactionService:
    return TransactionService(session)


def get_category_service(session: Session = Depends(get_session)) -> CategoryService:
    return CategoryService(session)


def get_stats_service(session: Session = Depends(get_session)) -> StatsService:
    return StatsService(session)
