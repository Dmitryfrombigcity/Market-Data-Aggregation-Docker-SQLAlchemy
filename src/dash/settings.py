from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.utils import instantiate


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    SERVER_PORT: int = Field(default=8050)


setting = instantiate(Settings)
