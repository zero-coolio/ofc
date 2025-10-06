# OFC Backend (be)

FastAPI + SQLModel backend for managing transactions, categories, and a balance dashboard.

## Quickstart
```bash
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload
```

## Tests
```bash
pytest -q
```

## Seed data
```bash
python scripts/seed_test_data.py
```

## Reset & seed
```bash
python scripts/reset_state.py
```
