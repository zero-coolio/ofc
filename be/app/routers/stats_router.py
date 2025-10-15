from fastapi import APIRouter, Depends
from typing import Optional, List
from datetime import datetime
from sqlmodel import Session
from app.database import get_session
from app.schemas import BalancePoint
from app.services import get_stats_service, StatsService
import logging

logger = logging.getLogger("ofc.routers.stats")

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/balance_over_time", response_model=List[BalancePoint])
def balance_over_time(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    svc: StatsService = Depends(get_stats_service),
):
    logger.info("➡️  balance_over_time called start=%s end=%s", start, end)
    points = svc.balance_over_time(start, end)
    logger.info(
        "✅  balance_over_time points=%s final_balance=%.2f",
        len(points),
        points[-1].balance if points else 0,
    )
    return points
