from abc import ABC, abstractmethod
from types import TracebackType

from app.db.db_connection import db_dependency
from app.repositories.dividends import DividendsRepository
from app.repositories.results_trades import ResultsTradesRepository


class UnitOfWorkBase(ABC):
    results_trades: ResultsTradesRepository
    dividends: DividendsRepository

    @abstractmethod
    def __init__(self) -> None:
        ...

    @abstractmethod
    async def __aenter__(self) -> None:
        ...

    @abstractmethod
    async def __aexit__(
            self,
            exception: type[BaseException] | None,
            value: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        ...

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...


class UnitOfWork(UnitOfWorkBase):
    def __init__(self, ) -> None:
        self.session_factory = db_dependency.session

    async def __aenter__(self) -> None:
        self.session = self.session_factory()
        self.results_trades = ResultsTradesRepository(self.session)
        self.dividends = DividendsRepository(self.session)

    async def __aexit__(
            self,
            exception: type[BaseException] | None,
            value: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        if exception:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()
        # await self.session_factory.remove()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
