from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from app.database import get_engine, get_session, init_db
from sqlalchemy import Engine

engine: Engine = init_db("-ut.db")

from app.main import app


# Use a dedicated sqlite file for this test run


def override_get_session():
    with Session(engine) as session:
        yield session


# Bind the app to our test database engine
app.dependency_overrides[get_session] = override_get_session

# Ensure a clean schema before the test
SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)

client = TestClient(app)


def test_create_user_then_reset_db():
    # 1) Bootstrap first user
    r = client.post("/users", json={"email": "reset@example.com", "name": "Reset User"})
    assert r.status_code == 201, r.text
    api_key = r.json()["api_key"]

    # Validate with /users/me
    r = client.get("/users/me", headers={"X-API-Key": api_key})
    assert r.status_code == 200
    assert r.json()["email"] == "reset@example.com"

    # 2) Reset DB (drop & recreate all tables)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    # 3) Old API key can't be used now (no users exist)
    r = client.get("/users/me", headers={"X-API-Key": api_key})
    assert r.status_code == 400  # "No users exist..."

    # 4) Bootstrap again with a new user
    r = client.post("/users", json={"email": "reset2@example.com", "name": "Reset Two"})
    assert r.status_code == 201, r.text
    api_key2 = r.json()["api_key"]
    assert api_key2 != api_key

    # New key works
    r = client.get("/users/me", headers={"X-API-Key": api_key2})
    assert r.status_code == 200
    assert r.json()["email"] == "reset2@example.com"
