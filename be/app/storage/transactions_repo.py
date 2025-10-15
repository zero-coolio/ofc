from typing import Optional, List, Sequence
from datetime import datetime
from sqlmodel import Session as SqlSession
from .base import BaseRepository
from app.models import Transaction
from typing import Optional
from app.database import open_session

from sqlmodel import Field, Session, SQLModel, create_engine, select

from fastapi import FastAPI, Depends, HTTPException, status
from app.database import get_session


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: SqlSession):
        super().__init__(session, Transaction)

    def list_filtered(
            self,
            category: Optional[str] = None,
            txn_type: Optional[str] = None,
            start: Optional[datetime] = None,
            end: Optional[datetime] = None,
    ) -> List[Transaction]:
        q = select(Transaction)
        if category:
            q = q.where(Transaction.category == category)
        if txn_type:
            q = q.where(Transaction.txn_type == txn_type)
        if start:
            q = q.where(Transaction.occurred_at >= start)
        if end:
            q = q.where(Transaction.occurred_at < end)
        q = q.order_by(Transaction.occurred_at)
        r = self.session.exec(q)
        s: Sequence[Transaction] = r.all()
        l: List[Transaction] = list(s)
        return l
