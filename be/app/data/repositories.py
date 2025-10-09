from typing import Optional, List
from datetime import date
from sqlmodel import Session, select
from app.models import User, Category, Transaction, Kind


class UserRepo:
    def __init__(self, session: Session):
        self.session = session

    def first(self) -> Optional[User]:
        return self.session.exec(select(User).order_by(User.id)).first()

    def get_by_api_key(self, api_key: str) -> Optional[User]:
        return self.session.exec(select(User).where(User.api_key == api_key)).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.exec(select(User).where(User.email == email)).first()

    def create(self, email: str, name: Optional[str], api_key: str) -> User:
        user = User(email=email, name=name, api_key=api_key)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user


class CategoryRepo:
    def __init__(self, session: Session):
        self.session = session

    def list_for_user(self, user_id: int) -> List[Category]:
        return self.session.exec(
            select(Category).where(Category.user_id == user_id).order_by(Category.name)
        ).all()

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.session.get(Category, category_id)

    def get_by_name_for_user(self, user_id: int, name: str) -> Optional[Category]:
        return self.session.exec(
            select(Category).where(Category.user_id == user_id, Category.name == name)
        ).first()

    def create(self, user_id: int, name: str) -> Category:
        cat = Category(user_id=user_id, name=name)
        self.session.add(cat)
        self.session.commit()
        self.session.refresh(cat)
        return cat

    def delete(self, category: Category) -> None:
        self.session.delete(category)
        self.session.commit()


class TransactionRepo:
    def __init__(self, session: Session):
        self.session = session

    def list_for_user(
        self,
        user_id: int,
        kind: Optional[Kind] = None,
        category_id: Optional[int] = None,
    ) -> List[Transaction]:
        stmt = select(Transaction).where(Transaction.user_id == user_id)
        if kind:
            stmt = stmt.where(Transaction.kind == kind)
        if category_id is not None:
            stmt = stmt.where(Transaction.category_id == category_id)
        stmt = stmt.order_by(Transaction.occurred_at, Transaction.id)
        return self.session.exec(stmt).all()

    def list_in_range_for_user(
        self, user_id: int, start: Optional[date], end: Optional[date]
    ) -> List[Transaction]:
        stmt = select(Transaction).where(Transaction.user_id == user_id)
        if start:
            stmt = stmt.where(Transaction.occurred_at >= start)
        if end:
            stmt = stmt.where(Transaction.occurred_at <= end)
        stmt = stmt.order_by(Transaction.occurred_at, Transaction.id)
        return self.session.exec(stmt).all()

    def get_by_id(self, tx_id: int) -> Optional[Transaction]:
        return self.session.get(Transaction, tx_id)

    def create(
        self,
        user_id: int,
        *,
        amount: float,
        kind: Kind,
        occurred_at: date,
        description: Optional[str],
        category_id: Optional[int]
    ) -> Transaction:
        tx = Transaction(
            user_id=user_id,
            amount=amount,
            kind=kind,
            occurred_at=occurred_at,
            description=description,
            category_id=category_id,
        )
        self.session.add(tx)
        self.session.commit()
        self.session.refresh(tx)
        return tx

    def update(self, tx: Transaction, **fields) -> Transaction:
        for k, v in fields.items():
            setattr(tx, k, v)
        self.session.add(tx)
        self.session.commit()
        self.session.refresh(tx)
        return tx

    def delete(self, tx: Transaction) -> None:
        self.session.delete(tx)
        self.session.commit()
