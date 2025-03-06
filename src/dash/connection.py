from typing import Iterator

import psycopg
from psycopg import Connection

from src.db.config import setting


def get_connection() -> Iterator[Connection]:
    with psycopg.connect(conninfo=setting.uri) as conn:
        yield conn


connection = get_connection()
conn = next(connection)
