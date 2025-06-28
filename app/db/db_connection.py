from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.db.config import setting


class DBDependency:
    def __init__(self) -> None:
        self.engine = create_async_engine(
            url=setting.url,
            # echo=True,
            pool_size=setting.POOL_MAX_SIZE,
            max_overflow=50,
            # echo_pool="debug"
        )

        self.session = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )


db_dependency = DBDependency()
