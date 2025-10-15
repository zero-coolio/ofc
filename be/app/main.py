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

BUILD_TIME = os.getenv("BUILD_TIME", "unknown")


# --- Health endpoints ---
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ofc-backend",
        "time": datetime.utcnow().isoformat() + "Z",
        "build_time": BUILD_TIME,
    }


@app.get("/createdb")
def createdb():
    init_db()
    return {
        "status": "ok",
        "service": "ofc-backend",
        "time": datetime.utcnow
