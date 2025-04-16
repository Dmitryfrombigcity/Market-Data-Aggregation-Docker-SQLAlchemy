import datetime
from typing import Sequence, Any

from sqlalchemy import select, func, or_, and_, column, Row, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import ResultsTrades, Dividends
from app.repositories.base_repository import SQLAlchemyRepository


class ResultsTradesRepository(SQLAlchemyRepository[ResultsTrades]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=ResultsTrades)

    async def db_read_flag(self, data: str) -> Any:
        flag = await self.session.scalar(
            select(func.max(self.model.last_page))
            .group_by(self.model.ticker)
            .having(self.model.ticker == data)
        )
        return flag

    async def db_read_dates(self, start: datetime.date) -> Sequence[datetime.date]:
        dates = await self.session.execute(
            select(self.model.trade_date.distinct())
            .filter(self.model.trade_date >= start)
            .order_by(self.model.trade_date)
        )
        dates_results = dates.scalars().all()
        return dates_results

    async def db_read_data_for_calculation(
            self,
            ticker: str,
            dividends_purchase_day_offset: int
    ) -> Sequence[Row[Any]]:

        subq = (
            select(Dividends)
            .select_from(Dividends)
            .filter(Dividends.ticker == ticker)
            .subquery()
        )
        cte = (
            select(self.model.trade_date, self.model.ticker, self.model.closing_price, column("value"))
            .join(subq, self.model.trade_date ==
                  subq.c.registry_closing_date + datetime.timedelta(days=dividends_purchase_day_offset))
            .filter(or_(self.model.ticker == ticker, self.model.ticker == 'day_off'))
            .cte()
        )
        subg_1 = (
            select(func.min(self.model.trade_date))
            .filter(self.model.ticker == ticker)
            .scalar_subquery()
        )
        stmt: Select[Any] = (
            select(self.model.trade_date, self.model.ticker, self.model.closing_price, column("value"))
            .select_from(self.model)
            .join(cte, self.model.trade_date == cte.c.trade_date, isouter=True)
            .filter(
                and_(
                    self.model.trade_date >= subg_1, or_(
                        self.model.ticker == ticker, self.model.ticker == 'day_off'
                    )
                )
            )
            .order_by(self.model.trade_date)
        )
        data_for_calculation = await self.session.execute(stmt)
        data_for_calculation_results = data_for_calculation.all()

        return data_for_calculation_results
