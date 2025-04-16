import datetime
from asyncio import TaskGroup
from types import TracebackType
from typing import Self

from loguru import logger

from app.aiohttp.connection import connection
from app.aiohttp.models import Page, ResultData, PagesHistory, ResultDividends
from app.aiohttp.settings import URL_HISTORY, URL_DIVIDENDS
from app.db.models.models import ResultsTrades, Dividends
from app.db.schemas.schemas import ResultsTradesScheme, DividendsScheme
from app.services.unitofwork import UnitOfWork


class DataCollectionService:
    def __init__(self) -> None:
        self.res_id = self.div_id = self.res_date = None
        self.uow: UnitOfWork | None = None

    async def __aenter__(self, uow: UnitOfWork | None = None) -> Self:
        self.uow = UnitOfWork() if uow is None else uow
        assert self.uow is not None  # mypy
        await self.uow.__aenter__()
        self.res_id = await self.uow.results_trades.db_read_max_by_attr("id")
        self.div_id = await self.uow.dividends.db_read_max_by_attr("id")
        self.res_date = await self.uow.results_trades.db_read_max_by_attr("trade_date")
        return self

    async def __aexit__(
            self,
            exception: type[BaseException] | None,
            value: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        assert self.uow is not None  # mypy
        if exception:
            try:
                await self.uow.results_trades.db_restore("id", self.res_id)
                await self.uow.dividends.db_restore("id", self.div_id)
            except BaseException:
                logger.error(
                    f"Unable to roll back tables. Manual rollback required. "
                    f"results_trades => max_id={self.res_id if self.res_id is not None else 0} "
                    f"dividends => max_id={self.div_id} "
                )
                raise
        await self.uow.session.commit()
        await self.uow.session.close()

    async def collect_information(self, ticker: str, pages: Page) -> None:
        """collecting information from pages"""

        async with TaskGroup() as group:
            for index in range(
                    pages.ind, pages.total, pages.pagesize
            ):
                group.create_task(self.get_information(ticker, index))

    async def get_information(
            self,
            ticker: str,
            index: int = 0,
            uow: UnitOfWork | None = None
    ) -> tuple[str, Page]:
        """getting the information from a page"""

        uow = UnitOfWork() if uow is None else uow
        async with uow:
            data_block, pages = await self._helper_get_information(ticker, index)

            # checking for updates
            if not index:
                new_index = await uow.results_trades.db_read_flag(ticker)
                if new_index:
                    pages = Page(new_index, pages.total, pages.pagesize)
                    return ticker, pages

            data_mod: list[ResultsTrades] = []
            for item in data_block.history.data:
                model = ResultsTradesScheme.model_validate(item, from_attributes=True)
                data_mod.append(
                    ResultsTrades(
                        **model.model_dump(),
                        last_page=pages.total
                    )
                )
            await uow.results_trades.db_update(data_mod)
        return ticker, pages

    @staticmethod
    async def _helper_get_information(
            ticker: str,
            index: int = 0
    ) -> tuple[ResultData, Page]:
        session = await anext(connection)
        try:
            async with session.get(f'{URL_HISTORY}{ticker}.json?start={index}') as response:
                response.raise_for_status()
                data_block = ResultData.model_validate_json(await response.text())
                pages_block = PagesHistory.model_validate_json(await response.text())
                pages = pages_block.history_cursor.data.pages_info
        except Exception as err:
            logger.exception(err)
            raise
        return data_block, pages

    async def get_dividends(
            self,
            ticker: str,
            uow: UnitOfWork | None = None
    ) -> None:
        """getting the information about dividends"""

        uow = UnitOfWork() if uow is None else uow
        async with uow:
            data_block = await self._helper_get_dividends(ticker)
            flag = await uow.dividends.db_read_flag(ticker)
            record = flag if flag else 0
            data_mod: list[Dividends] = []
            for item in data_block.dividends.data:
                model = DividendsScheme.model_validate(item, from_attributes=True)
                data_mod.append(Dividends(**model.model_dump()))
            await uow.dividends.db_update(data_mod[record:])

    @staticmethod
    async def _helper_get_dividends(
            ticker: str
    ) -> ResultDividends:
        session = await anext(connection)
        try:
            async with session.get(f'{URL_DIVIDENDS}{ticker}/dividends.json') as response:
                data_block = ResultDividends.model_validate_json(await response.text())
        except Exception as err:
            logger.exception(err)
            raise
        return data_block

    async def insert_days_off(
            self,
            start_date: datetime.date | None,
            uow: UnitOfWork | None = None
    ) -> None:
        """Inserting days-off into the table"""

        uow = UnitOfWork() if uow is None else uow
        async with uow:
            date_range = await uow.results_trades.db_read_dates(
                datetime.date.fromisocalendar(1, 1, 1) if start_date is None else start_date
            )
            date_set = self._helper_insert_days_off(date_range[-0] if start_date is None else start_date,
                                                    date_range[-1])
            date_set.difference_update(date_range)
            date_set_diff = {
                ResultsTrades(trade_date=date, ticker="day_off") for date in date_set
            }
            await uow.results_trades.db_update(date_set_diff)

    @staticmethod
    def _helper_insert_days_off(start: datetime.date, end: datetime.date) -> set[datetime.date]:
        date_set: set[datetime.date] = set()
        day = start
        while True:
            date_set.add(day)
            day += datetime.timedelta(days=1)
            if day > end:
                break
        return date_set
