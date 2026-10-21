from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SECRET_KEY = "change-me-to-a-random-value-at-least-32-bytes-long"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://altsmanager:altsmanager@localhost:5432/altsmanager"
    secret_key: str = DEFAULT_SECRET_KEY
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
    cors_origins: str = "http://localhost:3000"
    max_upload_size_bytes: int = 25 * 1024 * 1024
    allowed_document_content_types: str = (
        "application/pdf,"
        "image/png,image/jpeg,image/heic,image/webp,"
        "application/vnd.ms-excel,"
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,"
        "application/msword,"
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document,"
        "text/csv,text/plain"
    )
    login_rate_limit_attempts: int = 5
    login_rate_limit_window_seconds: int = 300

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def allowed_document_content_type_list(self) -> list[str]:
        return [ct.strip() for ct in self.allowed_document_content_types.split(",") if ct.strip()]

    def model_post_init(self, __context: object) -> None:
        key_is_weak = self.secret_key == DEFAULT_SECRET_KEY or len(self.secret_key) < 32
        if self.is_production and key_is_weak:
            raise RuntimeError(
                "SECRET_KEY must be set to a unique random value (at least 32 bytes) "
                "when ENVIRONMENT=production. Refusing to start with the default/placeholder key."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()
