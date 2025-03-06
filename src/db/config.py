from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.utils import instantiate


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    DB_HOST: str
    DB_PORT: int = Field(alias='POSTGRES_PORT')
    DB_USER: str
    DB_PASS: SecretStr
    DB_NAME: str
    POOL_MAX_SIZE: int = Field(default=50)

    @property
    def uri(self) -> str:
        return f'postgresql://{self.DB_USER}:{self.DB_PASS.get_secret_value()}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


setting = instantiate(Settings)
