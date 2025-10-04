from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import categories, transactions, dashboard, import_export, users, ws

app = FastAPI(title="OFC Transactions API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)
app.include_router(import_export.router)
app.include_router(users.router)
app.include_router(ws.router)


@app.get("/health")
def health():
    return {"status": "ok"}
