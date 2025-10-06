from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

init_db()
client = TestClient(app)

def test_full_flow():
    r = client.post("/users", json={"email": "u1@example.com", "name": "U1"})
    assert r.status_code == 201, "Run tests on a fresh DB for determinism"
    api_key = r.json()["api_key"]
    headers = {"X-API-Key": api_key}

    r = client.post("/categories", json={"name": "Income"}, headers=headers)
    assert r.status_code == 201, r.text
    cat_income = r.json()

    r = client.post("/transactions", json={
        "amount": 1000.0, "kind": "credit", "occurred_at": "2025-10-01",
        "description": "Paycheck", "category_id": cat_income["id"]
    }, headers=headers)
    assert r.status_code == 201, r.text

    r = client.post("/categories", json={"name": "Groceries"}, headers=headers)
    assert r.status_code == 201, r.text
    cat_gro = r.json()

    r = client.post("/transactions", json={
        "amount": 50.0, "kind": "debit", "occurred_at": "2025-10-02",
        "description": "Milk", "category_id": cat_gro["id"]
    }, headers=headers)
    assert r.status_code == 201, r.text

    r = client.get("/transactions", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 2

    r = client.get("/dashboard/balance?group_by=day", headers=headers)
    assert r.status_code == 200
    series = r.json()
    assert series[-1]["balance"] == 950.0
