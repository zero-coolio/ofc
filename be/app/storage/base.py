from typing import Generic, TypeVar, Type, Optional
from sqlmodel import SQLModel, Session

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def add(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get(self, pk: int) -> Optional[T]:
        return self.session.get(self.model, pk)

    def delete(self, obj: T) -> None:
        self.session.delete(obj)
        self.session.commit()
