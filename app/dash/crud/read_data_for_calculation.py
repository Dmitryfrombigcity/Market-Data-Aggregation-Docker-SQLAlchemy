import datetime
from typing import Sequence, Any

from sqlalchemy import Row, select, or_, column, Select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import ResultsTrades, Dividends


class ResultsTradesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = ResultsTrades

    async def db_read_data_for_calculation(
            self,
            ticker: str,
            date_min,
            date_max,
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

        stmt: Select[Any] = (
            select(self.model.trade_date, self.model.ticker, self.model.closing_price, column("value"))
            .select_from(self.model)
            .join(cte, self.model.trade_date == cte.c.trade_date, isouter=True)
            .filter(
                and_(
                    self.model.trade_date <= date_max,
                    self.model.trade_date >= date_min, or_(
                        self.model.ticker == ticker, self.model.ticker == 'day_off'
                    )
                )
            )
            .order_by(self.model.trade_date)
        )
        data_for_calculation = await self.session.execute(stmt)
        data_for_calculation_results = data_for_calculation.all()

        return data_for_calculation_results
