import asyncio
import sys
from asyncio import TaskGroup
from time import perf_counter
from typing import Any, Iterable

from loguru import logger

from app.aiohttp.connection import connection as http_conn
from app.services.data_collection import DataCollectionService
from app.services.data_processing import DataProcessingService
from logs.config import config
from project_settings import setting

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main(tickers: Iterable[str]) -> None:
    try:
        # collecting information from the website
        async with DataCollectionService() as dc_service:
            tasks: list[asyncio.Task[Any]] = []
            async with asyncio.TaskGroup() as group:
                for ticker in tickers:
                    tasks.append(
                        group.create_task(dc_service.get_information(ticker))
                    )
                    group.create_task(dc_service.get_dividends(ticker))
                for task in asyncio.as_completed(tasks):
                    ticker, pages = await task
                    group.create_task(dc_service.collect_information(ticker, pages))
            await dc_service.insert_days_off(dc_service.res_date)

        # closing the session
        await http_conn.aclose()

        logger.info('Collecting information has completed')
        print('Collecting information has completed')

        # processing of information
        async with DataProcessingService() as dp_service:
            async with TaskGroup() as group:
                for ticker in tickers:
                    group.create_task(dp_service.data_processing(ticker))

            logger.info('Processing of information has completed')
            print('Processing of information has completed')

    except BaseException as err:
        logger.error(repr(err))
        print('>>> An error occurred. Please see the log.', repr(err))


if __name__ == '__main__':
    logger.configure(**config)  # type:ignore
    logger.info('Starting...')
    tickers = setting.BUNCH_OF_TICKERS
    start = perf_counter()
    asyncio.run(main(tickers))
    logger.info('Ending...')
    print(perf_counter() - start)
