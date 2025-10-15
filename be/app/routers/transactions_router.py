from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from datetime import datetime

from app.schemas import TransactionCreate, TransactionRead, TransactionsResponse
from app.services import get_transaction_service, TransactionService
import logging

logger = logging.getLogger("ofc.routers.transactions")

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionRead, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    svc: TransactionService = Depends(get_transaction_service),
):
    p = payload.model_dump()
    logger.error(f"-----create_transaction called payload={p}")
    created = svc.create(payload)
    logger.info("✅  create_transaction completed id=%s", created.id)
    return TransactionRead(**created.model_dump())


@router.get("", response_model=TransactionsResponse)
def list_transactions(
    category: Optional[str] = None,
    txn_type: Optional[str] = Query("credit", description="credit or debit"),
    start: Optional[datetime] = datetime(2020, 1, 1),
    end: Optional[datetime] = None,  # datetime.now(),
    limit: int = 100,
    offset: int = 0,
    svc: TransactionService = Depends(get_transaction_service),
):
    logger.info(
        "➡️  list_transactions params category=%s type=%s start=%s end=%s limit=%s offset=%s",
        category,
        txn_type,
        start,
        end,
        limit,
        offset,
    )
    items, total = svc.list(category, txn_type, start, end, limit, offset)
    logger.info("✅  list_transactions returned=%s items", total)
    return {"items": [TransactionRead(**i.model_dump()) for i in items], "total": total}


@router.delete("/{tx_id}", status_code=204)
def delete_transaction(
    tx_id: int, svc: TransactionService = Depends(get_transaction_service)
):
    logger.info("➡️  delete_transaction called id=%s", tx_id)
    ok = svc.delete(tx_id)
    if not ok:
        logger.warning("❌ delete_transaction not_found id=%s", tx_id)
        raise HTTPException(status_code=404, detail="Transaction not found")
    logger.info("✅  delete_transaction ok id=%s", tx_id)
    return
