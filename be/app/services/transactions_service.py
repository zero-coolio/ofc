from typing import Optional, List, Tuple
from datetime import datetime
from sqlmodel import Session

from ..database import get_session
from ..models import Transaction
from ..schemas import TransactionCreate
from ..storage.transactions_repo import TransactionRepository
from .categories_service import CategoryService
import logging

log = logging.getLogger("ofc.services.transactions")


class TransactionService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = TransactionRepository(session)
        self.categories = CategoryService(session)

    def _normalize_type(self, t: str) -> str:
        t_norm = (t or "").strip().lower()
        if t_norm not in ("credit", "debit"):
            log.error(f"Invalid transaction type: {t}")
            raise ValueError(f"Invalid transaction trx_type: [{t}] ")
        return t_norm

    def create(self, payload: TransactionCreate) -> Transaction:
        log.error(f"$$$$$$$$$$$$$$ Service: create called payload=[{payload.model_dump()}")
        t_type = self._normalize_type(payload.txn_type)
        if payload.category and payload.category.strip():
            self.categories.create_if_missing(payload.category.strip())
        amount = payload.amount if t_type == "credit" else -abs(payload.amount)
        tx = Transaction(
            amount=amount,
            txn_type=t_type,
            description=payload.description,
            category=payload.category.strip() if payload.category else None,
            occurred_at=payload.occurred_at,
        )
        created = self.repo.add(tx)
        log.info("🧩 Service: transaction created -> %s", created.model_dump())
        return created

    def list(
            self,
            category: Optional[str] = None,
            type_: Optional[str] = None,
            start: Optional[datetime] = None,
            end: Optional[datetime] = None,
            limit: int = 100,
            offset: int = 0,
    ) -> Tuple[List[Transaction], int]:
        try:
            if type_:
                type_ = self._normalize_type(type_)
            log.info(
                "🧩 Service: list called category=%s type=%s start=%s end=%s limit=%s offset=%s",
                category,
                type_,
                start,
                end,
                limit,
                offset,
            )
            all_items = self.repo.list_filtered(category, type_, start, end)
            total = len(all_items)
            items = all_items[offset: offset + limit]
            return items, total

        except Exception as e:
            log.error("<UNK>  list_transactions exception=%s", e)
            raise e

    def delete(self, tx_id: int) -> bool:
        log.info("🧩 Service: delete called id=%s", tx_id)
        tx = self.repo.get(tx_id)
        if not tx:
            return False
        self.repo.delete(tx)
        return True
