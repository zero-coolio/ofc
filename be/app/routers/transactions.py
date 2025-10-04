from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select, Session
from typing import Optional

from app.database import get_session
from app.models import Transaction, Category, Kind as ModelKind, User
from app.schemas import TransactionCreate, TransactionRead, TransactionUpdate
from app.security import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if payload.category_id is not None:
        cat = session.get(Category, payload.category_id)
        if not cat or cat.user_id != user.id:
            raise HTTPException(status_code=400, detail="Invalid category_id")

    tx = Transaction(user_id=user.id, **payload.model_dump())
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return tx


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
    kind: Optional[ModelKind] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
):
    stmt = select(Transaction).where(Transaction.user_id == user.id)
    if kind:
        stmt = stmt.where(Transaction.kind == kind)
    if category_id is not None:
        stmt = stmt.where(Transaction.category_id == category_id)
    stmt = stmt.order_by(Transaction.occurred_at, Transaction.id)
    return session.exec(stmt).all()


@router.get("/{tx_id}", response_model=TransactionRead)
def get_transaction(
    tx_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    tx = session.get(Transaction, tx_id)
    if not tx or tx.user_id != user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.patch("/{tx_id}", response_model=TransactionRead)
def update_transaction(
    tx_id: int,
    payload: TransactionUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    tx = session.get(Transaction, tx_id)
    if not tx or tx.user_id != user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data and data["category_id"] is not None:
        cat = session.get(Category, data["category_id"])
        if not cat or cat.user_id != user.id:
            raise HTTPException(status_code=400, detail="Invalid category_id")

    for k, v in data.items():
        setattr(tx, k, v)
    session.add(tx)
    session.commit()
    session.refresh(tx)
    return tx


@router.delete("/{tx_id}", status_code=204)
def delete_transaction(
    tx_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    tx = session.get(Transaction, tx_id)
    if not tx or tx.user_id != user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(tx)
    session.commit()
    return
