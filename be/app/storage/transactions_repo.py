
from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, select
from .base import BaseRepository
from ..models import Transaction

class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: Session):
        super().__init__(session, Transaction)

    def list_filtered(self, category: Optional[str]=None, type_: Optional[str]=None, start: Optional[datetime]=None, end: Optional[datetime]=None) -> List[Transaction]:
        q = select(Transaction)
        if category:
            q = q.where(Transaction.category == category)
        if type_:
            q = q.where(Transaction.type == type_)
        if start:
            q = q.where(Transaction.occurred_at >= start)
        if end:
            q = q.where(Transaction.occurred_at < end)
        q = q.order_by(Transaction.occurred_at.asc())
        return self.session.exec(q).all()
