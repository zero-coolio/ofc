"""
Create and seed the SQLite database with Category and Transaction data.

Usage:
  python -m app.scripts.seed_db --reset --rows 100
"""

import argparse
import os
import random
from datetime import datetime, timedelta
from sqlmodel import Session, select

from app.database import init_db, open_session, DEFAULT_SQLITE_PATH, DATABASE_URL
from app.models import Category, Transaction

DEFAULT_CATEGORIES = [
    "groceries", "rent", "salary", "entertainment",
    "utilities", "transport", "eating out", "misc"
]

DESCRIPTIONS = [
    "Grocery run", "Monthly rent", "Paycheck", "Movie night",
    "Electric bill", "Bus pass", "Coffee", "Lunch out", "Gym",
    "Streaming", "Car fuel", "Phone bill", "Water bill"
]


def seed_categories(session: Session, names=None):
    """Insert categories if they don't exist."""
    names = names or DEFAULT_CATEGORIES
    existing = {c.name for c in session.exec(select(Category)).all()}
    to_create = [nm for nm in names if nm not in existing]

    for nm in to_create:
        session.add(Category(name=nm))

    session.commit()
    print(f"✅ Categories: {len(names)} total ({len(to_create)} new)")
    return names


def seed_transactions(session: Session, categories, rows: int):
    """Generate and insert random transactions."""
    now = datetime.utcnow()
    added = 0

    for _ in range(rows):
        txn_type = "credit" if random.random() < 0.3 else "debit"
        cat = random.choice(categories)
        amount = round(
            random.uniform(200, 2500) if txn_type == "credit"
            else random.uniform(5, 120), 2
        )
        desc = random.choice(DESCRIPTIONS)
        days_ago = random.randint(0, 60)
        minutes_offset = random.randint(0, 24 * 60)
        occurred_at = now - timedelta(days=days_ago, minutes=minutes_offset)

        tx = Transaction(
            amount=amount,
            txn_type=txn_type,
            description=desc,
            category=cat,
            occurred_at=occurred_at,
        )
        session.add(tx)
        added += 1

        if added % 100 == 0:
            session.commit()

    session.commit()
    print(f"✅ Transactions: {added} inserted.")


def main():
    parser = argparse.ArgumentParser(description="Seed SQLite database.")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate tables.")
    parser.add_argument("--rows", type=int, default=50, help="Number of transactions.")
    args = parser.parse_args()

    init_db()  # force_reset=args.reset)

    with open_session() as session:
        cats = seed_categories(session)
        seed_transactions(session, cats, args.rows)

    print(f"📄 SQLite file: {os.path.abspath(DEFAULT_SQLITE_PATH)}")
    print(f"🗄️  DB URL: {DATABASE_URL}")
    print("✅ Database seeding complete.")


if __name__ == "__main__":
    main()
