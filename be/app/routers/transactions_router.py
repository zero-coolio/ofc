from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional

from app.database import get_session
from app.models import Kind as ModelKind, User
from app.schemas import TransactionCreate, TransactionRead, TransactionUpdate
from app.security import get_current_user
from app.services import transactions_service as svc
from datetime import datetime, timezone
from datetime import datetime, timezone

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        return svc.create_transaction(session, user_id=user.id, **payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
    kind: Optional[ModelKind] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
):
    return svc.list_transactions(
        session, user_id=user.id, kind=kind, category_id=category_id
    )


@router.get("/{tx_id}", response_model=TransactionRead)
def get_transaction(
    tx_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        return svc.get_transaction(session, user_id=user.id, tx_id=tx_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Transaction not found")


@router.patch("/{tx_id}", response_model=TransactionRead)
def update_transaction(
    tx_id: int,
    payload: TransactionUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        return svc.update_transaction(
            session,
            user_id=user.id,
            tx_id=tx_id,
            **payload.model_dump(exclude_unset=True)
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Transaction not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{tx_id}", status_code=204)
def delete_transaction(
    tx_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        svc.delete_transaction(session, user_id=user.id, tx_id=tx_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return


class Transaction:

    def __init__(
        self,
        id: str,
        amount,
        kind: str,
        occurred_at: str,  # YYYY-MM-DD
        description: str,
        category_id: str = "NAN",  # 0 if null
        # RFC3339
    ):
        self.id = id
        self.amount = amount
        self.kind = kind
        self.occurred_at = occurred_at
        self.description = description
        self.category_id = category_id

        self.created_at = now_utc = datetime.now(timezone.utc)
