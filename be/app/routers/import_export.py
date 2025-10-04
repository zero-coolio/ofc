import csv
import io
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.database import get_session
from app.models import Transaction, Category, Kind as ModelKind, User

router = APIRouter(prefix="/io", tags=["import-export"])


@router.post("/import/csv")
async def import_csv(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    user: User = Depends(
        __import__("app.security", fromlist=["get_current_user"]).get_current_user
    ),
):
    """
    Import transactions from a CSV file with headers:
    occurred_at (YYYY-MM-DD), amount, kind (credit|debit), description, category
    If category doesn't exist, it will be created.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    content = (await file.read()).decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(content))

    created = 0
    for row in reader:
        try:
            occurred_at = datetime.strptime(row["occurred_at"], "%Y-%m-%d").date()
            amount = float(row["amount"])
            kind = row["kind"].strip().lower()
            if kind not in ("credit", "debit"):
                raise ValueError("invalid kind")
            description = row.get("description") or None
            cat_name = (row.get("category") or "").strip() or None
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid row: {row}. Error: {e}"
            )

        category_id: Optional[int] = None
        if cat_name:
            cat = session.exec(
                select(Category).where(
                    Category.user_id == user.id, Category.name == cat_name
                )
            ).first()
            if not cat:
                cat = Category(name=cat_name)
                session.add(cat)
                session.commit()
                session.refresh(cat)
            category_id = cat.id

        tx = Transaction(
            user_id=user.id,
            amount=amount,
            kind=ModelKind(kind),
            occurred_at=occurred_at,
            description=description,
            category_id=category_id,
        )
        session.add(tx)
        created += 1

    session.commit()
    return {"imported": created}


@router.get("/export/csv")
def export_csv(
    session: Session = Depends(get_session),
    user: User = Depends(
        __import__("app.security", fromlist=["get_current_user"]).get_current_user
    ),
):
    """
    Export all transactions to CSV with headers:
    id,occurred_at,amount,kind,description,category
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "occurred_at", "amount", "kind", "description", "category"])

    stmt = (
        select(Transaction)
        .where(Transaction.user_id == user.id)
        .order_by(Transaction.occurred_at, Transaction.id)
    )
    for tx in session.exec(stmt).all():
        cat_name = None
        if tx.category_id:
            cat = session.get(Category, tx.category_id)
            cat_name = cat.name if cat else None
        writer.writerow(
            [
                tx.id,
                tx.occurred_at.isoformat(),
                f"{tx.amount:.2f}",
                tx.kind.value,
                tx.description or "",
                cat_name or "",
            ]
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.read()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="transactions.csv"'},
    )
