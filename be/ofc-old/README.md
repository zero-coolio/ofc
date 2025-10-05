# FastAPI Transactions App

A small FastAPI app to manage credits/debits, categorize them, and view a basic dashboard of balance over time.

## Features
- CRUD for **Transactions** (credits and debits)
- CRUD for **Categories**
- Assign transactions to categories
- Dashboard endpoint that returns a time-series of **cumulative balance**
- Simple HTML dashboard (served at `/dashboard`) that charts balance over time

## Tech
- Python 3.10+
- FastAPI
- SQLModel (SQLite)
- Uvicorn

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:
- Interactive API docs: http://127.0.0.1:8000/docs
- Simple dashboard:     http://127.0.0.1:8000/dashboard

## Useful Endpoints
- `POST /categories` | `GET /categories`
- `POST /transactions` | `GET /transactions`
- `GET /dashboard/balance` — balance time series (query params: `start`, `end`, `group_by=day|week|month`)
- `GET /dashboard` — basic HTML chart

## Example payloads

Create a category:
```json
{
  "name": "Groceries"
}
```

Create a transaction (credit):
```json
{
  "amount": 1000.0,
  "kind": "credit",
  "occurred_at": "2025-10-01",
  "description": "Paycheck",
  "category_id": null
}
```

Create a transaction (debit):
```json
{
  "amount": 55.30,
  "kind": "debit",
  "occurred_at": "2025-10-02",
  "description": "Whole Foods",
  "category_id": 1
}
```

## Notes
- Debits reduce balance; credits increase it.
- The balance series is cumulative over time, filling missing periods with the last known balance.
---

## Authentication (optional)
Set an environment variable `API_KEY` to require clients to send `X-API-Key` header.
If `API_KEY` is not set, the API is open (no auth).

```bash
export API_KEY="your-secret"
uvicorn app.main:app --reload
```

## CSV Import/Export
- `POST /io/import/csv` — upload a `.csv` file with headers:
  `occurred_at,amount,kind,description,category`
- `GET /io/export/csv` — downloads all transactions as CSV.

## Tests
Run unit tests with pytest:
```bash
pytest -q
```
---

## Multi-user model
- Each user has an API key. All data (categories, transactions) is **scoped per user**.
- First-run bootstrap:
  1. Start the server
  2. Call `POST /users` with `{ "email": "you@example.com", "name": "You" }` to create the first user.
  3. Save the returned `api_key` and send it in the `X-API-Key` header for all subsequent requests.
- To add more users later, call `POST /users/create` with any valid `X-API-Key`.

### Required headers (after bootstrap)
```
X-API-Key: <user-api-key>
```

### Affected endpoints
All existing endpoints now act **per user**:
- `/categories` (CRUD) — only your categories
- `/transactions` (CRUD) — only your transactions
- `/dashboard/balance` — balance derived from your transactions
- `/io/import/csv`, `/io/export/csv` — import/export only your data
- `/users/me` — return your user object
---

## WebSocket: live transaction stream
Endpoint: `GET ws://127.0.0.1:8000/ws/transactions?api_key=YOUR_KEY&since=2025-10-01T00:00:00Z`

- Auth: pass `api_key` as a query param (or `X-API-Key` header if your WS client supports custom headers).
- Messages:
  - `{"type":"transaction","data":{...}}` per transaction (initial backlog, then new ones)
  - `{"type":"ready"}` once the initial backlog has been sent
  - send `"ping"` to receive `"pong"`

## Protobuf
Schema file: `protos/transaction.proto`

To generate Python code (requires `protoc` installed):
```bash
pip install protobuf
python -m pip install grpcio-tools  # optional if you prefer grpc_tools.protoc

# Using protoc
protoc -I protos --python_out=app/protos protos/transaction.proto

# or using grpc_tools.protoc
python -m grpc_tools.protoc -I protos --python_out=app/protos protos/transaction.proto
```

This will create `app/protos/transaction_pb2.py`. You can then serialize a transaction like:
```python
from app.protos import transaction_pb2
msg = transaction_pb2.Transaction(
    id=1, amount=1000.0, kind=transaction_pb2.CREDIT,
    occurred_at="2025-10-01", description="Paycheck",
    category_id=0, created_at="2025-10-01T12:00:00Z"
)
payload = msg.SerializeToString()  # send as binary on the websocket if desired
```
