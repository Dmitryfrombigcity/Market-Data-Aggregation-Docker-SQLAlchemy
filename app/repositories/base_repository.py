from abc import ABC, abstractmethod
from typing import Any, Iterable

from sqlalchemy import select, Result, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.base import Base


class AbstractRepository(ABC):
    @abstractmethod
    async def db_update(self, data: Iterable[Base]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def db_read(self, data: dict[str, Any] | None = None) -> Result[Any]:
        raise NotImplementedError


class SQLAlchemyRepository[T: Base](AbstractRepository):
    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    async def db_update(self, data: Iterable[Base]) -> None:
        self.session.add_all(data)

    async def db_read_max_by_attr(self, attr: str) -> Any:
        max_attr = await self.session.scalar(
            select(func.max(getattr(self.model, attr)))
        )
        return max_attr

    async def db_restore(
            self,
            attr: str,
            max_attr: int | None
    ) -> None:
        max_attr = 0 if max_attr is None else max_attr
        await self.session.execute(
            delete(self.model)
            .filter(getattr(self.model, attr) > max_attr)
        )

    async def db_read(self, data: dict[str, Any] | None = None) -> Result[Any]:
        stm = select(self.model)
        if data is not None:
            stm = stm.filter_by(**data)
        res = await self.session.execute(stm)
        return res
