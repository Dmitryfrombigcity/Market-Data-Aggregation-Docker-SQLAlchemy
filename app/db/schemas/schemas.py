import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


class ResultsTradesScheme(BaseModel):
    trade_date: Annotated[datetime.date, Field(alias="TRADEDATE")]
    ticker: Annotated[str, Field(alias="SECID")]
    closing_price: Annotated[Decimal | None, Field(alias="CLOSE")]


class DividendsScheme(BaseModel):
    registry_closing_date: Annotated[datetime.date, Field(alias="registry_closedate")]
    ticker: Annotated[str, Field(alias="secid")]
    value: Annotated[Decimal | None, Field(alias="value")]
