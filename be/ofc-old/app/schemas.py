from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class Kind(str, Enum):
    credit = "credit"
    debit = "debit"


class UserCreate(BaseModel):
    email: str
    name: Optional[str] = None


class UserRead(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    api_key: str
    created_at: datetime


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CategoryRead(BaseModel):
    id: int
    name: str
    created_at: datetime


class TransactionCreate(BaseModel):
    amount: float = Field(gt=0)
    kind: Kind
    occurred_at: date
    description: Optional[str] = None
    category_id: Optional[int] = None


class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0)
    kind: Optional[Kind] = None
    occurred_at: Optional[date] = None
    description: Optional[str] = None
    category_id: Optional[int] = None


class TransactionRead(BaseModel):
    id: int
    amount: float
    kind: Kind
    occurred_at: date
    description: Optional[str] = None
    category_id: Optional[int] = None
    created_at: datetime


class BalancePoint(BaseModel):
    label: str
    balance: float
