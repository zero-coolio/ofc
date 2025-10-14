from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import transactions_router, stats_router, categories_router
from sqlmodel import SQLModel
from app.database import engine, init_db
import logging, sys, os
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ofc")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup:init_db (via lifespan)")
    init_db()
    yield
    logger.info("shutdown:cleanup complete (via lifespan)")


app = FastAPI(title="OFC Transactions API", version="3.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BUILD_TIME = os.getenv("BUILD_TIME", "unknown")


@app.get("/health")
def health():
    return {
        "status"    : "ok",
        "service"   : "ofc-backend",
        "time"      : datetime.utcnow().isoformat() + "Z",
        "build_time": BUILD_TIME,
    }


@app.get("/info")
def info():
    return {"name": "Stephen Leonard", "email": "steve.j.leonard@gmail.com"}


@app.post("/reset-db")
def reset_db():
    logger.warning("⚠️  RESET-DB endpoint called: dropping and recreating all tables.")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    logger.info("✅  RESET-DB completed successfully.")
    return {"ok": True, "message": "Database reset complete"}


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

app.include_router(transactions_router.router)
app.include_router(stats_router.router)
app.include_router(categories_router.router)
