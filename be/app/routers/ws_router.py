import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from sqlmodel import Session, select

from app.database import engine
from app.models import Transaction, User

router = APIRouter(prefix="/ws", tags=["websocket"])


async def authenticate_ws(websocket: WebSocket, session: Session) -> User:
    api_key = websocket.query_params.get("api_key") or websocket.headers.get("x-api-key")
    if not api_key:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)
    user = session.exec(select(User).where(User.api_key == api_key)).first()
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)
    return user


@router.websocket("/transactions")
async def transactions_stream(websocket: WebSocket):
    await websocket.accept()
    with Session(engine) as session:
        user = await authenticate_ws(websocket, session)

        since = websocket.query_params.get("since")
        bookmark: Optional[datetime] = None
        if since:
            try:
                bookmark = datetime.fromisoformat(since.replace("Z", "+00:00"))
            except Exception:
                await websocket.send_json({"type": "error", "error": "invalid_since"})
                bookmark = None

        poll_interval = 1.0
        sent_ids = set()

        rows = session.exec(select(Transaction).where(Transaction.user_id == user.id).order_by(Transaction.created_at, Transaction.id)).all()
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

        await websocket.send_json({"type": "ready"})

        try:
            while True:
                await asyncio.sleep(poll_interval)
                new_rows = session.exec(select(Transaction).where(Transaction.user_id == user.id).order_by(Transaction.created_at, Transaction.id)).all()
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
                            "created_at": tx.created_at.replace(tzinfo=None).isoformat() + "Z",
                        },
                    }
                    await websocket.send_json(payload)
                    sent_ids.add(tx.id)
        except WebSocketDisconnect:
            return
