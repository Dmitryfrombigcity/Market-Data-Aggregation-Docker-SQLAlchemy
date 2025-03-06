import datetime
from decimal import Decimal
from typing import NamedTuple


class Record(NamedTuple):
    trade_date: datetime.date
    ticker: str
    closing_price: Decimal
    value: Decimal


class Flag(NamedTuple):
    value: int
