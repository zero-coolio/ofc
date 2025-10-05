import io
import json
import time
from fastapi.testclient import TestClient

from app.main import app

from app.database import init_db

# Make sure the DB schema exists before tests run
init_db()

client = TestClient(app)


def bootstrap_user():
    # Create the first user (bootstrap)
    r = client.post("/users", json={"email": "u1@example.com", "name": "U1"})
    assert r.status_code in (201, 403)
    if r.status_code == 201:
        return r.json()["api_key"]
    else:
        # if already bootstrapped (e.g., another test ran first), we need to create another via /users/create
        # but to call /users/create we need *some* api key; fetch via a quick invalid call and return None
        # For deterministic tests, we'll instead just skip obtaining a second key here.
        # In our test order, we call bootstrap_user once at the top.
        raise RuntimeError("User already bootstrapped; test order issue.")


def test_full_flow():
    api_key = bootstrap_user()
    headers = {"X-API-Key": api_key}

    # Create category
    r = client.post("/categories", json={"name": "Income"}, headers=headers)
    assert r.status_code == 201, r.text
    cat_income = r.json()

    # Create transactions
    r = client.post("/transactions", json={
        "amount"     : 1000.0, "kind": "credit", "occurred_at": "2025-10-01", "description": "Paycheck",
        "category_id": cat_income["id"]
    }, headers=headers)
    assert r.status_code == 201, r.text
    t1 = r.json()

    r = client.post("/categories", json={"name": "Groceries"}, headers=headers)
    assert r.status_code == 201, r.text
    cat_gro = r.json()

    r = client.post("/transactions", json={
        "amount"     : 50.0, "kind": "debit", "occurred_at": "2025-10-02", "description": "Milk",
        "category_id": cat_gro["id"]
    }, headers=headers)
    assert r.status_code == 201, r.text
    t2 = r.json()

    # List transactions
    r = client.get("/transactions", headers=headers)
    assert r.status_code == 200
    txs = r.json()
    assert len(txs) == 2

    # Dashboard balance
    r = client.get("/dashboard/balance?group_by=day", headers=headers)
    assert r.status_code == 200, r.text
    series = r.json()
    assert series[-1]["balance"] == 950.0, series

    # Export CSV
    r = client.get("/io/export/csv", headers=headers)
    assert r.status_code == 200
    csv_text = r.text
    assert "Paycheck" in csv_text and "Milk" in csv_text

    # Import CSV (add one more credit)
    csv_payload = "occurred_at,amount,kind,description,category\n2025-10-03,25.00,credit,Gift,\n"
    files = {"file": ("import.csv", csv_payload, "text/csv")}
    r = client.post("/io/import/csv", headers=headers, files=files)
    assert r.status_code == 200, r.text
    assert r.json()["imported"] == 1

    # Confirm new balance
    r = client.get("/dashboard/balance?group_by=day", headers=headers)
    series2 = r.json()
    assert series2[-1]["balance"] == 975.0, series2

    # Websocket smoke test — receive "ready"
    with client.websocket_connect(f"/ws/transactions?api_key={api_key}") as ws:
        msg = ws.receive_json()
        assert msg.get("type") in ("transaction", "ready")
        # It's OK if we get a 'transaction' first due to backlog; we should soon get 'ready' too
        if msg.get("type") != "ready":
            msg2 = ws.receive_json()
            assert msg2.get("type") == "ready"
