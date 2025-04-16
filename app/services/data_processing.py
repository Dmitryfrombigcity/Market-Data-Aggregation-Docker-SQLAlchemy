from datetime import timedelta
from decimal import Decimal
from types import TracebackType
from typing import Self

from loguru import logger

from app.db.models.models import ProcessedData
from app.services.unitofwork import UnitOfWork
from project_settings import setting


class DataProcessingService:

    async def __aenter__(self, uow: UnitOfWork | None = None) -> Self:
        await self.truncate()
        return self

    async def __aexit__(
            self,
            exception: type[BaseException] | None,
            value: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        if exception:
            try:
                await self.truncate()
            except BaseException:
                logger.error(
                    f"Unable to truncate the processed_data table. Manual truncate required. "
                )

    @staticmethod
    async def truncate(
            uow: UnitOfWork | None = None
    ) -> None:
        """ TRUNCATE processed_data RESTART IDENTITY"""

        uow = UnitOfWork() if uow is None else uow
        async with uow:
            await uow.data_processing.db_truncate()

    @staticmethod
    async def data_processing(
            ticker: str,
            uow: UnitOfWork | None = None
    ) -> None:
        """processing of data according to specified settings"""

        uow = UnitOfWork() if uow is None else uow

        async with uow:
            shares = 0
            monthly_balance = expenses = Decimal(0)
            day = setting.MONTHLY_PURCHASE_DAY
            dividends = None
            sentinel = setting.LIMIT_OF_DAYS_FOR_PRICE_SEARCH

            new_records: list[ProcessedData] = []

            data = await uow.results_trades.db_read_data_for_calculation(
                ticker, dividends_purchase_day_offset=setting.DIVIDENDS_PURCHASE_DAY_OFFSET)
            for record in data:
                date, _, price, value = record
                dividends = value if not dividends else dividends

                if dividends:
                    if price:
                        income = dividends * shares
                        shares = shares + (income + monthly_balance) // price
                        monthly_balance = (income + monthly_balance) % price

                        dividends = None

                if day == date.day:
                    if price:
                        expenses += setting.MONTHLY_INVESTMENTS
                        shares = shares + (setting.MONTHLY_INVESTMENTS + monthly_balance) // price
                        monthly_balance = (setting.MONTHLY_INVESTMENTS + monthly_balance) % price

                        day = setting.MONTHLY_PURCHASE_DAY
                        sentinel = setting.LIMIT_OF_DAYS_FOR_PRICE_SEARCH
                    else:
                        day = (date + timedelta(days=1)).day
                        sentinel -= 1
                        if not sentinel:
                            break

                if not price:
                    continue

                capitalization = shares * price

                new_records.append(
                    ProcessedData(
                        date=date,
                        ticker=ticker,
                        expenses=expenses,
                        shares=shares,
                        capitalization=capitalization,
                        price=price,
                        monthly_balance=monthly_balance
                    )
                )

            await uow.data_processing.db_update(new_records)
