from asyncio import current_task

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_scoped_session

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
        # self.engine_ = create_engine(url=setting.url)

        self.session = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )
        # self.scoped_session = async_scoped_session(
        #     self.session,
        #     current_task
        # )


db_dependency = DBDependency()
