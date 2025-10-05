import csv, io
from datetime import datetime
from typing import Optional
from sqlmodel import Session
from app.data.repositories import CategoryRepo, TransactionRepo
from app.models import Kind as ModelKind

def import_transactions_csv(session: Session, *, user_id: int, csv_text: str) -> int:
    reader = csv.DictReader(io.StringIO(csv_text))
    created = 0
    cat_repo = CategoryRepo(session)
    tx_repo = TransactionRepo(session)

    for row in reader:
        occurred_at = datetime.strptime(row["occurred_at"], "%Y-%m-%d").date()
        amount = float(row["amount"])
        kind = row["kind"].strip().lower()
        if kind not in ("credit", "debit"):
            raise ValueError("invalid kind")
        description = row.get("description") or None
        cat_name = (row.get("category") or "").strip() or None

        category_id: Optional[int] = None
        if cat_name:
            cat = cat_repo.get_by_name_for_user(user_id, cat_name)
            if not cat:
                cat = cat_repo.create(user_id=user_id, name=cat_name)
            category_id = cat.id

        tx_repo.create(
            user_id=user_id, amount=amount, kind=ModelKind(kind),
            occurred_at=occurred_at, description=description, category_id=category_id
        )
        created += 1
    return created

def export_transactions_csv(session: Session, *, user_id: int) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "occurred_at", "amount", "kind", "description", "category"])

    tx_repo = TransactionRepo(session)
    cat_repo = CategoryRepo(session)
    for tx in tx_repo.list_for_user(user_id):
        cat_name = ""
        if tx.category_id:
            cat = cat_repo.get_by_id(tx.category_id)
            cat_name = cat.name if cat else ""
        writer.writerow([
            tx.id,
            tx.occurred_at.isoformat(),
            f"{tx.amount:.2f}",
            tx.kind.value,
            tx.description or "",
            cat_name,
        ])
    return output.getvalue()
