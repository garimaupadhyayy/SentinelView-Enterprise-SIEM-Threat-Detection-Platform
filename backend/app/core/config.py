"""
Central application configuration, loaded from environment variables
(see .env.example). Uses pydantic-settings so every value is validated
and typed at startup rather than failing deep inside a request handler.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "SentinelView"
    ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Auth ---
    JWT_SECRET_KEY: str = "change-me-in-production-please"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # --- Database (MySQL) ---
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "sentinel"
    MYSQL_PASSWORD: str = "sentinel_dev_password"
    MYSQL_DB: str = "sentinelview"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"
        )

    # --- Redis ---
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # --- Ingestion agent ---
    INGEST_API_KEY: str = "change-me-shared-secret"

    # --- Alerting integrations (optional) ---
    ALERT_WEBHOOK_URL: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    ALERT_EMAIL_FROM: str = ""
    ALERT_EMAIL_TO: str = ""

    # --- Threat intel (nice-to-have) ---
    ABUSEIPDB_API_KEY: str = ""
    GEOIP_LOOKUP_URL: str = "http://ip-api.com/json/{ip}"

    # --- Dedup / correlation windows (seconds) ---
    ALERT_DEDUP_WINDOW_SECONDS: int = 300
    BRUTE_FORCE_WINDOW_SECONDS: int = 300
    BRUTE_FORCE_THRESHOLD: int = 5
    PORT_SCAN_WINDOW_SECONDS: int = 60
    PORT_SCAN_DISTINCT_PORTS: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
