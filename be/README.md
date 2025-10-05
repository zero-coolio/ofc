# OFC (Open Finance Controller)

A clean FastAPI app to manage credits/debits, categories, and view a balance-over-time dashboard.
Multi-user with per-user API keys. Includes CSV import/export, WebSocket streaming, and a protobuf schema.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload
```
