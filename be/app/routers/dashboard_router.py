from datetime import date
from typing import Literal, List

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlmodel import Session

from app.database import get_session
from app.security import get_current_user
from app.models import User
from app.schemas import BalancePoint
from app.services import dashboard_service as svc

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/balance", response_model=List[BalancePoint])
def balance_series(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    group_by: Literal["day", "week", "month"] = Query(default="day"),
):
    return svc.balance_series(
        session, user_id=user.id, start=start, end=end, group_by=group_by
    )


@router.get("", response_class=HTMLResponse)
def dashboard_page():
    return "<h2>OFC Dashboard</h2><p>Use <code>/dashboard/balance</code> for JSON time series.</p>"
