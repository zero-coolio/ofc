from collections import defaultdict
from datetime import date, timedelta
from typing import Literal, List
from app.models import Kind as ModelKind
from app.schemas import BalancePoint
from .transactions_service import list_in_range


def floor_to_period(d: date, group_by: Literal["day", "week", "month"]) -> date:
    if group_by == "day":
        return d
    if group_by == "week":
        return d - timedelta(days=d.weekday())
    if group_by == "month":
        return d.replace(day=1)
    raise ValueError("invalid group_by")


def balance_series(
    session,
    *,
    user_id: int,
    start: date | None,
    end: date | None,
    group_by: Literal["day", "week", "month"] = "day"
) -> List[BalancePoint]:
    txs = list_in_range(session, user_id=user_id, start=start, end=end)
    buckets = defaultdict(float)
    min_d = None
    max_d = None
    for tx in txs:
        signed = tx.amount if tx.kind == ModelKind.credit else -tx.amount
        p = floor_to_period(tx.occurred_at, group_by)
        buckets[p] += signed
        if min_d is None or tx.occurred_at < min_d:
            min_d = tx.occurred_at
        if max_d is None or tx.occurred_at > max_d:
            max_d = tx.occurred_at
    if min_d is None:
        return []

    def next_period(d: date) -> date:
        if group_by == "day":
            return d + timedelta(days=1)
        if group_by == "week":
            return d + timedelta(days=7)
        if group_by == "month":
            return (
                d.replace(year=d.year + 1, month=1, day=1)
                if d.month == 12
                else d.replace(month=d.month + 1, day=1)
            )

    series: List[BalancePoint] = []
    running = 0.0
    cur = floor_to_period(min_d, group_by)
    last = floor_to_period(max_d, group_by)
    while cur <= last:
        running += buckets.get(cur, 0.0)
        series.append(BalancePoint(label=cur.isoformat(), balance=round(running, 2)))
        cur = next_period(cur)
    return series
