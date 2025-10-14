
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, UniqueConstraint

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    __table_args__ = (UniqueConstraint("name", name="uq_category_name"),)

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    type: str
    description: str
    category: Optional[str] = Field(default=None, index=True)
    occurred_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
