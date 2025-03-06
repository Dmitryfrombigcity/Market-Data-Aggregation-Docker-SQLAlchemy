from asyncio import TaskGroup
from typing import Any, cast

from loguru import logger
from psycopg import sql

from src.aiohttp.connection import connection
from src.aiohttp.settings import URL_HISTORY, URL_DIVIDENDS
from src.db.crud import db_read, db_update
from src.db.queries import check_for_updates, insert_results_of_trades, check_for_dividends, insert_dividends, \
    truncate
from src.db.schemas import Flag
from src.pydantic.models import Page, ResultData, PagesHistory, ResultDividends


async def get_information(ticker: str, index: int = 0) -> tuple[str, Page]:
    """getting the information from a page"""

    session = await anext(connection)
    try:
        async with session.get(f'{URL_HISTORY}{ticker}.json?start={index}') as response:
            response.raise_for_status()
            data_block = ResultData.model_validate_json(await response.text())
            pages_block = PagesHistory.model_validate_json(await response.text())
            pages = pages_block.history_cursor.data.pages_info
    except Exception as err:
        logger.exception(err)
        query = sql.SQL(truncate).format(
            table=sql.Identifier('results_of_trades'))
        await db_update(query, [()])
        raise

    # checking for page updates
    if not index:
        flag = cast(list[Flag], await db_read(check_for_updates, (ticker,)))  # to satisfy mypy
        if flag:
            new_index = flag[0].value
            pages = Page(new_index, pages.total, pages.pagesize)
            return ticker, pages

    data_mod: list[tuple[Any, ...]] = []
    for item in data_block.history.data:
        data_mod.append(
            (item.TRADEDATE, item.SECID, item.CLOSE, pages.total)
        )
    await db_update(insert_results_of_trades, data_mod)
    return ticker, pages


async def get_dividends(ticker: str, ) -> None:
    """getting the information about dividends"""

    session = await anext(connection)
    try:
        async with session.get(f'{URL_DIVIDENDS}{ticker}/dividends.json') as response:
            data_block = ResultDividends.model_validate_json(await response.text())
    except Exception as err:
        logger.exception(err)
        query = sql.SQL(truncate).format(
            table=sql.Identifier('dividends'))
        await db_update(query, [()])
        raise
    else:
        flag = cast(list[Flag], await db_read(check_for_dividends, (ticker,)))  # to satisfy mypy
        record = flag[0].value if flag else 0
        data_mod: list[tuple[Any, ...]] = []
        for item in data_block.dividends.data:
            data_mod.append((item.registry_closedate, item.secid, item.value))
        await db_update(insert_dividends, data_mod[record:])


async def collect_information(ticker: str, pages: Page, ) -> None:
    """collecting information from pages"""

    async with TaskGroup() as group:
        for index in range(
                pages.ind, pages.total, pages.pagesize
        ):
            group.create_task(get_information(ticker, index))
