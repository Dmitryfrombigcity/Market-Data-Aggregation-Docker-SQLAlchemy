from typing import Any, NamedTuple, Iterable

from loguru import logger
from psycopg import sql
from psycopg.abc import Query
from psycopg.errors import Error, DuplicateTable
from psycopg.rows import namedtuple_row
from psycopg.sql import Composed

from src.db.connection import connection
from src.db.queries import truncate


async def db_update(
        query: Composed | str,
        data: Iterable[tuple[Any, ...]]
) -> None:
    pool = await anext(connection)
    try:
        async with pool.connection() as aconn:
            async with aconn.cursor() as acur:
                await acur.executemany(query, data)
    except Error as err:
        logger.exception(err)
        raise


async def db_create(query: str | Composed) -> None:
    pool = await anext(connection)
    try:
        async with pool.connection() as aconn:
            await aconn.execute(query)
    except DuplicateTable:
        query_truncate = sql.SQL(truncate).format(
            table=sql.Identifier('processed_data'))
        await db_update(query_truncate, [()])
    except Error as err:
        logger.exception(err)
        raise


async def db_read(
        query: Query,
        data: tuple[Any, ...] | dict[str, Any] = tuple()
) -> list[NamedTuple]:
    pool = await anext(connection)
    try:
        async with pool.connection() as aconn:
            async with aconn.cursor(row_factory=namedtuple_row) as acur:
                await acur.execute(query, data)
                return await acur.fetchall()

    except Error as err:
        logger.exception(err)
        raise
