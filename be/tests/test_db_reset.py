from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from app.main import app
from app.database import get_session

TEST_DB_URL = "sqlite:///./ofc_ut_reset.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})

def override_get_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session
SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)

client = TestClient(app)

def test_create_user_then_reset_db():
    r = client.post("/users", json={"email": "reset@example.com", "name": "Reset User"})
    assert r.status_code == 201, r.text
    api_key = r.json()["api_key"]

    r = client.get("/users/me", headers={"X-API-Key": api_key})
    assert r.status_code == 200

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    r = client.get("/users/me", headers={"X-API-Key": api_key})
    assert r.status_code == 400

    r = client.post("/users", json={"email": "reset2@example.com", "name": "Reset Two"})
    assert r.status_code == 201
    api_key2 = r.json()["api_key"]
    assert api_key2 != api_key

    r = client.get("/users/me", headers={"X-API-Key": api_key2})
    assert r.status_code == 200
