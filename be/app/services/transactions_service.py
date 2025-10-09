from typing import Optional
from datetime import date
from sqlmodel import Session
from app.data.repositories import TransactionRepo, CategoryRepo
from app.models import Transaction, Kind


def create_transaction(
    session: Session,
    *,
    user_id: int,
    amount: float,
    kind: Kind,
    occurred_at: date,
    description: Optional[str],
    category_id: Optional[int]
) -> Transaction:
    if category_id is not None:
        cat = CategoryRepo(session).get_by_id(category_id)
        if not cat or cat.user_id != user_id:
            raise ValueError("Invalid category_id")
    return TransactionRepo(session).create(
        user_id=user_id,
        amount=amount,
        kind=kind,
        occurred_at=occurred_at,
        description=description,
        category_id=category_id,
    )


def list_transactions(
    session: Session,
    *,
    user_id: int,
    kind: Optional[Kind] = None,
    category_id: Optional[int] = None
):
    return TransactionRepo(session).list_for_user(user_id, kind, category_id)


def get_transaction(session: Session, *, user_id: int, tx_id: int):
    tx = TransactionRepo(session).get_by_id(tx_id)
    if not tx or tx.user_id != user_id:
        raise LookupError("Transaction not found")
    return tx


def update_transaction(session: Session, *, user_id: int, tx_id: int, **fields):
    tx = TransactionRepo(session).get_by_id(tx_id)
    if not tx or tx.user_id != user_id:
        raise LookupError("Transaction not found")
    if "category_id" in fields and fields["category_id"] is not None:
        cat = CategoryRepo(session).get_by_id(fields["category_id"])
        if not cat or cat.user_id != user_id:
            raise ValueError("Invalid category_id")
    return TransactionRepo(session).update(tx, **fields)


def delete_transaction(session: Session, *, user_id: int, tx_id: int):
    tx = TransactionRepo(session).get_by_id(tx_id)
    if not tx or tx.user_id != user_id:
        raise LookupError("Transaction not found")
    TransactionRepo(session).delete(tx)


def list_in_range(
    session: Session, *, user_id: int, start: Optional[date], end: Optional[date]
):
    return TransactionRepo(session).list_in_range_for_user(user_id, start, end)
