from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://altsmanager:altsmanager@localhost:5432/altsmanager"
    secret_key: str = "change-me-to-a-random-value-at-least-32-bytes-long"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    storage_backend: str = "local"
    document_storage_path: str = "./data/documents"
    s3_bucket: str = ""
    s3_region: str = "us-east-1"
    s3_endpoint_url: str | None = None
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    environment: str = "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
