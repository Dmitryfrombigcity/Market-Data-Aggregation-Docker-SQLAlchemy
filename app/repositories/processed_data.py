from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import ProcessedData
from app.repositories.base_repository import SQLAlchemyRepository


class ProcessedDataRepository(SQLAlchemyRepository[ProcessedData]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=ProcessedData)

    async def db_truncate(self) -> None:
        await self.session.execute(
            text("TRUNCATE processed_data RESTART IDENTITY")
        )
