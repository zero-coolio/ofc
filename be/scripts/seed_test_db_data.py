"""
Seed deterministic test data into SQLite for OFC.
Usage:
    python scripts/seed_test_data.py
Optional:
    OFC_DATABASE_URL=sqlite:///./ofc.db python scripts/seed_test_data.py
"""
import os
from datetime import datetime, date
from app.database import get_engine
from sqlmodel import Session, SQLModel, create_engine, select
from app.models import User, Category, Transaction, Kind


def get_or_create(session: Session, model, defaults=None, **filters):
    inst = session.exec(select(model).filter_by(**filters)).first()
    if inst:
        return inst, False
    inst = model(**filters, **(defaults or {}))
    session.add(inst)
    session.commit()
    session.refresh(inst)
    return inst, True


def seed():
    eng = get_engine()
    SQLModel.metadata.create_all(eng)
    with Session(eng) as s:
        # Users
        alice, _ = get_or_create(
            s, User,
            email="alice@example.com",
            defaults={
                "name"      : "Alice",
                "api_key"   : "alice-api-key-1111111111111111",
                "created_at": datetime.fromisoformat("2025-10-01T09:00:00"),
            },
        )
        bob, _ = get_or_create(
            s, User,
            email="bob@example.com",
            defaults={
                "name"      : "Bob",
                "api_key"   : "bob-api-key-2222222222222222",
                "created_at": datetime.fromisoformat("2025-10-01T09:05:00"),
            },
        )

        # Categories
        income_a, _ = get_or_create(s, Category, name="Income", user_id=alice.id)
        groc_a, _ = get_or_create(s, Category, name="Groceries", user_id=alice.id)
        rent_a, _ = get_or_create(s, Category, name="Rent", user_id=alice.id)
        income_b, _ = get_or_create(s, Category, name="Income", user_id=bob.id)
        trav_b, _ = get_or_create(s, Category, name="Travel", user_id=bob.id)

        # Transactions (Alice)
        get_or_create(
            s, Transaction,
            id=1,
            defaults=dict(
                amount=2000.00, kind=Kind.credit, occurred_at=date(2025, 10, 1),
                description="Paycheck", created_at=datetime.fromisoformat("2025-10-01T10:00:00"),
                user_id=alice.id, category_id=income_a.id
            ),
        )
        get_or_create(
            s, Transaction,
            id=2,
            defaults=dict(
                amount=75.50, kind=Kind.debit, occurred_at=date(2025, 10, 2),
                description="Groceries", created_at=datetime.fromisoformat("2025-10-02T12:00:00"),
                user_id=alice.id, category_id=groc_a.id
            ),
        )
        get_or_create(
            s, Transaction,
            id=3,
            defaults=dict(
                amount=1200.00, kind=Kind.debit, occurred_at=date(2025, 10, 3),
                description="October Rent", created_at=datetime.fromisoformat("2025-10-03T08:30:00"),
                user_id=alice.id, category_id=rent_a.id
            ),
        )
        get_or_create(
            s, Transaction,
            id=4,
            defaults=dict(
                amount=20.00, kind=Kind.debit, occurred_at=date(2025, 10, 4),
                description="Snacks", created_at=datetime.fromisoformat("2025-10-04T14:45:00"),
                user_id=alice.id, category_id=groc_a.id
            ),
        )

        # Transactions (Bob)
        get_or_create(
            s, Transaction,
            id=5,
            defaults=dict(
                amount=1500.00, kind=Kind.credit, occurred_at=date(2025, 10, 1),
                description="Paycheck", created_at=datetime.fromisoformat("2025-10-01T10:10:00"),
                user_id=bob.id, category_id=income_b.id
            ),
        )
        get_or_create(
            s, Transaction,
            id=6,
            defaults=dict(
                amount=300.00, kind=Kind.debit, occurred_at=date(2025, 10, 5),
                description="Flight", created_at=datetime.fromisoformat("2025-10-05T09:00:00"),
                user_id=bob.id, category_id=trav_b.id
            ),
        )


if __name__ == "__main__":
    seed()
    print("✅ Seeded deterministic test data into", get_engine().url)
