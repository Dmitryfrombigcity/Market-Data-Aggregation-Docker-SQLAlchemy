from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import Dividends
from app.repositories.base_repository import SQLAlchemyRepository


class DividendsRepository(SQLAlchemyRepository[Dividends]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Dividends)

    async def db_read_flag(self, data: str) -> int | None:
        flag = await self.session.scalar(
            select(func.count())
            .select_from(self.model)
            .group_by(self.model.ticker)
            .having(self.model.ticker == data)
        )
        return flag
