from typing import AsyncGenerator


import aiohttp
from loguru import logger

from app.aiohttp.settings import HEADERS, setting


async def get_session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    conn = aiohttp.TCPConnector(limit=setting.TCPConnectorLimit)
    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(
            headers=HEADERS,
            connector=conn,
            timeout=timeout
    ) as session:
        try:
            while True:
                yield session
        finally:
            logger.info("aiohttp.ClientSession has closed")


connection = get_session()
