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


