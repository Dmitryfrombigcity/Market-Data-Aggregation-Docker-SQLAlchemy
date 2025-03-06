import asyncio
import subprocess
import sys
from asyncio import TaskGroup
from pathlib import Path
from time import perf_counter
from typing import Any, Iterable

from loguru import logger

from logs.config import config
from project_settings import setting
from src.aiohttp.connection import connection as http_conn
from src.data_collection import get_information, get_dividends, collect_information
from src.data_processing import data_processing
from src.db.connection import connection as db_conn
from src.db.crud import db_update, db_create
from src.db.queries import results_of_trades, dividends, insert_days_off_to_results_of_trades, processed_data
from src.utils import start_db


async def main(tickers: Iterable[str]) -> None:
    try:
        # collecting information from the website
        await db_create(results_of_trades)
        await db_create(dividends)
        await db_create(processed_data)

        tasks: list[asyncio.Task[Any]] = []
        async with asyncio.TaskGroup() as group:
            for ticker in tickers:
                tasks.append(
                    group.create_task(get_information(ticker))
                )
                group.create_task(get_dividends(ticker))
            for task in asyncio.as_completed(tasks):
                ticker, pages = await task
                group.create_task(collect_information(ticker, pages))

        # closing the session
        await http_conn.aclose()
        logger.info('Collecting information has completed')
        print('Collecting information has completed')

        # modifying the collected information
        await db_update(insert_days_off_to_results_of_trades, [()])

        # processing of information
        async with TaskGroup() as group:
            for ticker in tickers:
                group.create_task(data_processing(ticker))
        logger.info('Processing of information has completed')
        print('Processing of information has completed')
        await db_conn.aclose()
        logger.info('AsyncConnectionPool has closed')

        path_to_dash = Path('.') / 'src' / 'dash' / 'dash_plotly.py'
        subprocess.run([
            sys.executable, path_to_dash],
        )

    except BaseException as err:
        logger.error(repr(err))
        print('>>> An error occurred. Please see the log.')


if __name__ == '__main__':
    logger.configure(**config)  # type:ignore
    logger.info('Starting...')
    tickers = setting.BUNCH_OF_TICKERS
    with start_db():
        print('done.')
        start = perf_counter()
        asyncio.run(main(tickers))
        logger.info('Ending...')
        print(perf_counter() - start)
