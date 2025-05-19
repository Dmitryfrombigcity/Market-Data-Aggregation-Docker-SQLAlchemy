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

    def __repr__(self):
        """ for tests"""
        return f"({self.trade_date}, {self.ticker}, {self.closing_price}, {self.last_page})"


class Dividends(IdMixin, Base):
    registry_closing_date: Mapped[datetime.date]
    ticker: Mapped[str]
    value: Mapped[Decimal]

    def __repr__(self):
        """ for tests"""
        return f"({self.registry_closing_date}, {self.ticker}, {self.value})"


