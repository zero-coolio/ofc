
from sqlmodel import Session
from .transactions_service import TransactionService
from .categories_service import CategoryService
from .stats_service import StatsService

def get_transaction_service(session: Session) -> TransactionService:
    return TransactionService(session)

def get_category_service(session: Session) -> CategoryService:
    return CategoryService(session)

def get_stats_service(session: Session) -> StatsService:
    return StatsService(session)
