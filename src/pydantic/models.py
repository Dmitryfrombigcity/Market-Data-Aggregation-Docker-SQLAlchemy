from typing import NamedTuple, Annotated

from pydantic import BaseModel, Field


# ----------------------------------

class TickerData(NamedTuple):
    BOARDID: str
    TRADEDATE: str
    SHORTNAME: str
    SECID: str
    NUMTRADES: float | None
    VALUE: float | None
    OPEN: float | None
    LOW: float | None
    HIGH: float | None
    LEGALCLOSEPRICE: float | None
    WAPRICE: float | None
    CLOSE: float | None
    VOLUME: float | None
    MARKETPRICE2: float | None
    MARKETPRICE3: float | None
    ADMITTEDQUOTE: float | None
    MP2VALTRD: float | None
    MARKETPRICE3TRADESVALUE: float | None
    ADMITTEDVALUE: float | None
    WAVAL: float | None
    TRADINGSESSION: float | None
    CURRENCYID: str
    TRENDCLSPR: float | None
    TRADE_SESSION_DATE: str | None


class TickersData(BaseModel):
    data: list[TickerData]


class ResultData(BaseModel):
    history: TickersData


# ----------------------------------

class Page(NamedTuple):
    ind: int
    total: int
    pagesize: int


class PageMod(NamedTuple):
    pages_info: Page


class Pages(BaseModel):
    data: PageMod


class PagesHistory(BaseModel):
    history_cursor: Annotated[Pages, Field(alias='history.cursor')]


# ----------------------------------

class Dividend(NamedTuple):
    secid: str
    isin: str
    registry_closedate: str
    value: float
    currencyid: str


class Dividends(BaseModel):
    data: list[Dividend]


class ResultDividends(BaseModel):
    dividends: Dividends
