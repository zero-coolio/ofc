from sqlmodel import Session

from app.models import User, Transaction, Kind as ModelKind
from sqlmodel import Session, select
from collections import defaultdict
from datetime import date, timedelta
from typing import Literal, List
from app.schemas import BalancePoint


class TransactionService:

    def __init__(self, session: Session):
        print("transaction_service")

    def next_period(self, d: date, group_by: Literal["day", "week", "month"]) -> date:
        if group_by == "day":
            return d + timedelta(days=1)
        if group_by == "week":
            return d + timedelta(days=7)
        if group_by == "month":
            if d.month == 12:
                return d.replace(year=d.year + 1, month=1, day=1)
            else:
                return d.replace(month=d.month + 1, day=1)
        raise ValueError("group_by must be 'day', 'week', 'month'")

    def floor_to_period(
            self, d: date, group_by: Literal["day", "week", "month"]
    ) -> date:
        if group_by == "day":
            return d
        if group_by == "week":
            # ISO week starts on Monday
            return d - timedelta(days=d.weekday())
        if group_by == "month":
            return d.replace(day=1)
        raise ValueError("invalid group_by")

    def get_transactions(
            self,
            start,
            end,
            user: User,
            session: Session,
            group_by: Literal["day", "week", "month"],
    ) -> List[BalancePoint]:
        # Fetch transactions in range (or all if not provided)
        stmt = select(Transaction).where(Transaction.user_id == user.id)
        if start:
            stmt = stmt.where(Transaction.occurred_at >= start)
        if end:
            stmt = stmt.where(Transaction.occurred_at <= end)
        stmt = stmt.order_by(Transaction.occurred_at, Transaction.id)

        txs = session.exec(stmt).all()

        # Group amounts by period using sign from kind
        buckets = defaultdict(float)
        min_d = None
        max_d = None

        for tx in txs:
            signed = tx.amount if tx.kind == ModelKind.credit else -tx.amount
            p = self.floor_to_period(tx.occurred_at, group_by)
            buckets[p] += signed
            if min_d is None or tx.occurred_at < min_d:
                min_d = tx.occurred_at
            if max_d is None or tx.occurred_at > max_d:
                max_d = tx.occurred_at

        if min_d is None:  # no data
            return []

        # Generate sorted periods

        series: List[BalancePoint] = []
        running = 0.0
        cur = self.floor_to_period(min_d, group_by)
        last = self.floor_to_period(max_d, group_by)

        while cur <= last:
            running += buckets.get(cur, 0.0)
            label = cur.isoformat()
            series.append(BalancePoint(label=label, balance=round(running, 2)))
            cur = self.next_period(cur)
        return series
