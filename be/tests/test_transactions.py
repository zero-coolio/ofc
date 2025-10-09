from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from app.database import get_engine, get_session, init_db
from sqlalchemy import Engine
from fastapi import Depends, FastAPI

engine: Engine = init_db("-ut.db")

from app.main import app
import pprint

API_URL = "http://localhost:8000"  # "https://<your-backend-url>.a.run.app/api"  # or
API_KEY = "your-api-key-here"

# --- SAMPLE TRANSACTION ---
transaction = {
    "amount": 123.45,
    "kind": "credit",  # or "debit"
    "occurred_at": "2025-10-07",
    "description": "Test transaction via script",
    "category_id": 1,
}

category = {"name": "Seafood Imports"}


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session

# Ensure a clean schema before the test
SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)

client = TestClient(app)


def test_simple_transaction():
    # 1) Bootstrap first user
    r = client.post("/users", json={"email": "reset@example.com", "name": "Reset User"})
    assert r.status_code == 201, r.text
    api_key = r.json()["api_key"]
    json = r.json()
    print()
    pprint.pprint(json)

    headers = {"X-API-Key": api_key}
    r = client.post(
        API_URL + "/categories", json={"name": "Frozen Fish"}, headers=headers
    )

    url = API_URL + "/transactions"
    r = client.post(f"{url}", json=transaction, headers=headers)
    json = r.json()
    print()
    pprint.pprint(json)
