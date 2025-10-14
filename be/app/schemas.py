
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class TransactionCreate(BaseModel):
    amount: float
    type: str
    description: str
    category: Optional[str] = None
    occurred_at: datetime = Field(..., description="ISO8601 datetime")

class TransactionRead(BaseModel):
    id: int
    amount: float
    type: str
    description: str
    category: Optional[str] = None
    occurred_at: datetime
    created_at: datetime

class BalancePoint(BaseModel):
    date: datetime
    balance: float

class TransactionsResponse(BaseModel):
    items: List[TransactionRead]
    total: int

class CategoryCreate(BaseModel):
    name: str

class CategoryRead(BaseModel):
    id: int
    name: str
    created_at: datetime
