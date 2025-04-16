from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils.utils import instantiate

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
URL_HISTORY = 'https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/'
URL_DIVIDENDS = 'https://iss.moex.com/iss/securities/'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    TCPConnectorLimit: Annotated[int, Field(default=100)]


setting = instantiate(Settings)
