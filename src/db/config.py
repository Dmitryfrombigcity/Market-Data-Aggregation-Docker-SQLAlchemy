from typing import Annotated

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.utils import instantiate


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    DB_HOST: Annotated[str, Field(default='localhost')]
    DB_PORT: Annotated[int, Field(alias='POSTGRES_PORT')]
    DB_USER: Annotated[str, Field(default='user')]
    DB_PASS: Annotated[SecretStr, Field(default='password')]
    DB_NAME: Annotated[str, Field(default='aggregation')]
    POOL_MAX_SIZE: Annotated[int, Field(default=50)]

    @property
    def uri(self) -> str:
        return f'postgresql://{self.DB_USER}:{self.DB_PASS.get_secret_value()}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


setting = instantiate(Settings)
