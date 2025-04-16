import datetime
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.mixin import IdMixin


class ResultsTrades(IdMixin, Base):
    trade_date: Mapped[datetime.date]
    ticker: Mapped[str]
    closing_price: Mapped[Decimal | None]
    last_page: Mapped[int | None]


class Dividends(IdMixin, Base):
    registry_closing_date: Mapped[datetime.date]
    ticker: Mapped[str]
    value: Mapped[Decimal]


class ProcessedData(IdMixin, Base):
    date: Mapped[datetime.date]
    ticker: Mapped[str]
    expenses: Mapped[Decimal]
    shares: Mapped[int]
    capitalization: Mapped[Decimal]
    price: Mapped[Decimal]
    monthly_balance: Mapped[Decimal]

