from decimal import Decimal
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode

from src.utils import instantiate


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    BUNCH_OF_TICKERS: Annotated[tuple[str, ...], NoDecode, Field(default='SBER, LKOH')]
    MONTHLY_INVESTMENTS: Annotated[Decimal, Field(default=Decimal(1000), gt=0)]
    DIVIDENDS_PURCHASE_DAY_OFFSET: Annotated[int, Field(default=8, ge=0, le=28)]
    MONTHLY_PURCHASE_DAY: Annotated[int, Field(default=1, ge=1, le=28)]
    LIMIT_OF_DAYS_FOR_PRICE_SEARCH: Annotated[int, Field(default=28, ge=1, le=28)]

    @field_validator('BUNCH_OF_TICKERS', mode='before')
    @classmethod
    def decode_numbers(cls, v: str) -> tuple[str, ...]:
        return tuple(str(x).strip() for x in v.split(','))


setting = instantiate(Settings)
