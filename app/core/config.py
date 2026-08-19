from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://altsmanager:altsmanager@localhost:5432/altsmanager"
    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    storage_backend: str = "local"
    document_storage_path: str = "./data/documents"


@lru_cache
def get_settings() -> Settings:
    return Settings()
