from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel

from app.routers import transactions_router, stats_router, categories_router
from app.database import engine, init_db, open_session
from app import models  # ensure models are registered with SQLModel metadata
from app.scripts.seed_db import seed_categories, seed_transactions

import logging, sys, os
from datetime import datetime

# --- Logging setup ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ofc")


# --- App lifespan (startup/shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup:init_db (via lifespan)")
    init_db()
    yield
    logger.info("shutdown:cleanup complete (via lifespan)")


# --- App instance ---
app = FastAPI(title="OFC Transactions API", version="3.4.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions_router.router)
app.include_router(stats_router.router)
app.include_router(categories_router.router)

BUILD_TIME = os.getenv("BUILD_TIME", "unknown")


# --- Health endpoints ---
@app.get("/health")
def health():
    return {
        "status"    : "ok",
        "service"   : "ofc-backend",
        "time"      : datetime.utcnow().isoformat() + "Z",
        "build_time": BUILD_TIME,
    }


@app.get("/createdb")
def createdb():
    init_db()
    return {
        "status"    : "ok",
        "service"   : "ofc-backend",
        "time"      : datetime.now().isoformat() + "Z",
        "build_time": BUILD_TIME,
    }


@app.get("/info")
def info():
    return {"name": "Stephen Leonard", "email": "steve.j.leonard@gmail.com"}


@app.get("/reset-db")
def reset_db():
    """
    Drop and recreate all tables, then seed categories and `rows` random transactions.
    Uses the existing seed_db.py logic. DEMO ONLY — destructive operation.
    """
    from app.scripts import seed_db  # import here to avoid circular imports

    logger.warning("⚠️  /reset-db called: dropping, recreating, and seeding database.")

    # Drop & recreate schema
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    logger.info("✅ Tables recreated successfully.")


@app.get("/seed")
def seed(rows: int = Query(50, ge=1, le=10000)):
    """
    Drop and recreate all tables, then seed categories and `rows` random transactions.
    Uses the existing seed_db.py logic. DEMO ONLY — destructive operation.
    """
    from app.scripts import seed_db  # import here to avoid circular imports

    # Run seed using your helper functions
    with open_session() as session:
        cats = seed_db.seed_categories(session)
        seed_db.seed_transactions(session, cats, rows)

    # Optional: quick summary
    try:
        from sqlmodel import select
        from app.models import Category, Transaction

        with open_session() as session:
            cat_count = session.exec(select(Category)).count()
            txn_count = session.exec(select(Transaction)).count()
    except Exception as e:
        logger.error(f"Error in seeding database: {e}")
        cat_count = txn_count = None

    logger.info(
        f"✅ Database seeded: {cat_count} categories, {txn_count} transactions."
    )
    return {
        "ok"          : True,
        "message"     : "Database reset and seeded successfully.",
        "categories"  : cat_count,
        "transactions": txn_count,
        "rows"        : rows,
    }


import json
from fastapi.responses import Response


@app.get("/dump-db")
def dump_db():
    """
    Return a full JSON dump of all database contents, human-readable (pretty-printed).
    Includes Category and Transaction tables.
    DEMO ONLY — not for production.
    """
    from sqlmodel import select
    from app.models import Category, Transaction

    with open_session() as session:
        categories = session.exec(select(Category)).all()
        transactions = session.exec(select(Transaction)).all()

        # Serialize objects to dictionaries
        cats_json = [c.model_dump() for c in categories]
        txns_json = [t.model_dump() for t in transactions]

    payload = {
        "ok"     : True,
        "summary": {
            "category_count"   : len(cats_json),
            "transaction_count": len(txns_json),
        },
        "tables" : {"categories": cats_json, "transactions": txns_json},
    }

    # Return pretty-printed JSON string
    return Response(
        content=json.dumps(payload, indent=2, default=str),
        media_type="application/json",
    )


def main():
    """
    Entry point for local execution (e.g. `python -m app.main`).
    Cloud Run uses gunicorn/uvicorn and will call the app object.
    """
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        log_level="info",
        reload=bool(os.getenv("DEV", False)),
    )


if __name__ == "__main__":
    main()
