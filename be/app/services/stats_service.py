from typing import List, Optional
from datetime import datetime
from ..schemas import BalancePoint
from ..storage.transactions_repo import TransactionRepository
from sqlmodel import Session
import logging

log = logging.getLogger("ofc.services.stats")


class StatsService:
    def __init__(self, session: Session):
        self.repo = TransactionRepository(session)

    def balance_over_time(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        #            txs_repo: TransactionRepository = D,
    ) -> List[BalancePoint]:
        log.info("🧩 Service: stats balance_over_time start=%s end=%s", start, end)
        txs = self.repo.list_filtered(start, end)
        balance = 0.0
        points: List[BalancePoint] = []
        for t in txs:
            balance += t.amount
            points.append(BalancePoint(date=t.occurred_at, balance=round(balance, 2)))
        if not points:
            from datetime import datetime as _dt

            points.append(BalancePoint(date=_dt.utcnow(), balance=0.0))
        return points
