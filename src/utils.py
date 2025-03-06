import subprocess
import sys
from contextlib import contextmanager
from time import sleep
from typing import Iterator, Type

from loguru import logger
from pydantic_core import ValidationError
from pydantic_settings import BaseSettings


@contextmanager
def start_db() -> Iterator[None]:
    """ database management"""

    subpr = subprocess.run(
        'docker compose -f postgrs_on_docker.yml up -d',
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )
    if subpr.returncode:
        print("Docker not found. Trying to connect to local database...")
        logger.error(subpr.stderr)
    print("Docker is starting...", end='')
    sleep(5)
    try:
        yield
    finally:
        subprocess.run(
            'docker compose -f postgrs_on_docker.yml down',
            stderr=subprocess.PIPE,
            shell=True
        )


def instantiate[T: BaseSettings](Settings: Type[T]) -> T:
    try:
        return Settings()
    except ValidationError as err:
        logger.remove()
        logger.add('logs/logging.txt')
        logger.exception(err)
        print(err)
        sys.exit(1)  # to avoid ImportError
