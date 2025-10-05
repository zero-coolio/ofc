import asyncio
from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    Query,
    HTTPException,
    status,
)
from sqlmodel import Session, select

from app.database import get_session
from app.models import Transaction, User
from app.security import get_current_user

router = APIRouter(prefix="/ws", tags=["websocket"])


async def authenticate_ws(websocket: WebSocket, session: Session) -> User:
    # Support auth via query param `api_key` (since many WS clients cannot send custom headers)
    api_key = websocket.query_params.get("api_key")
    if not api_key:
        # Also permit standard header if client supports it
        api_key = websocket.headers.get("x-api-key")
    if not api_key:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=401, detail="Missing API key")
    user = session.exec(select(User).where(User.api_key == api_key)).first()
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user


@router.websocket("/transactions")
async def transactions_stream(
    websocket: WebSocket,
    since: Optional[str] = Query(
        default=None,
        description="ISO timestamp; only stream items with created_at > since",
    ),
):
    # Accept the WS first so we can send errors if needed
    await websocket.accept()
    # Create a session per-connection
    from app.database import engine
    from sqlmodel import Session

    with Session(engine) as session:
        # Authenticate
        user = await authenticate_ws(websocket, session)

        # Parse 'since' bookmark
        bookmark: Optional[datetime] = None
        if since:
            try:
                bookmark = datetime.fromisoformat(since.replace("Z", "+00:00"))
            except Exception:
                await websocket.send_json({"type": "error", "error": "invalid_since"})
                bookmark = None

        # Streaming loop: send backlog, then poll for new rows
        poll_interval = 1.0  # seconds
        sent_ids = set()

        # Backlog
        query = (
            select(Transaction)
            .where(Transaction.user_id == user.id)
            .order_by(Transaction.created_at, Transaction.id)
        )
        rows = session.exec(query).all()
        for tx in rows:
            if bookmark and tx.created_at <= bookmark:
                continue
            payload = {
                "type": "transaction",
                "data": {
                    "id": tx.id,
                    "amount": tx.amount,
                    "kind": tx.kind.value,
                    "occurred_at": tx.occurred_at.isoformat(),
                    "description": tx.description,
                    "category_id": tx.category_id,
                    "created_at": tx.created_at.replace(tzinfo=None).isoformat() + "Z",
                },
            }
            await websocket.send_json(payload)
            sent_ids.add(tx.id)

        # Heartbeat
        await websocket.send_json({"type": "ready"})

        try:
            while True:
                await asyncio.sleep(poll_interval)
                # Check for new transactions
                stmt = (
                    select(Transaction)
                    .where(Transaction.user_id == user.id)
                    .order_by(Transaction.created_at, Transaction.id)
                )
                new_rows = session.exec(stmt).all()
                for tx in new_rows:
                    if tx.id in sent_ids:
                        continue
                    if bookmark and tx.created_at <= bookmark:
                        continue
                    payload = {
                        "type": "transaction",
                        "data": {
                            "id": tx.id,
                            "amount": tx.amount,
                            "kind": tx.kind.value,
                            "occurred_at": tx.occurred_at.isoformat(),
                            "description": tx.description,
                            "category_id": tx.category_id,
                            "created_at": tx.created_at.replace(tzinfo=None).isoformat()
                            + "Z",
                        },
                    }
                    await websocket.send_json(payload)
                    sent_ids.add(tx.id)

                # Also receive optional client pings/commands to keep the socket healthy
                try:
                    msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                    if msg == "ping":
                        await websocket.send_text("pong")
                except asyncio.TimeoutError:
                    pass
        except WebSocketDisconnect:
            return
