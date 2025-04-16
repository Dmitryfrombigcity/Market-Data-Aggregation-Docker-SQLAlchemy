import sys
from typing import Type

from loguru import logger
from pydantic_core import ValidationError
from pydantic_settings import BaseSettings


def instantiate[T: BaseSettings](Settings: Type[T]) -> T:
    try:
        return Settings()
    except ValidationError as err:
        logger.remove()
        logger.add('logs/logging.txt')
        logger.exception(err)
        print(err)
        sys.exit(1)  # to avoid ImportError
