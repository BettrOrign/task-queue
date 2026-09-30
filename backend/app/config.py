import os
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class Settings:
    """Application settings sourced from environment variables."""

    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_v1_str: str = os.getenv("API_V1_STR", "/api/v1")

    db_host: str = os.getenv("POSTGRES_HOST", "localhost")
    db_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    db_user: str = os.getenv("POSTGRES_USER", "taskqueue")
    db_password: str = os.getenv("POSTGRES_PASSWORD", "secret")
    db_name: str = os.getenv("POSTGRES_DB", "taskqueue")

    rabbitmq_host: str = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user: str = os.getenv("RABBITMQ_USER", "taskqueue")
    rabbitmq_password: str = os.getenv("RABBITMQ_PASSWORD", "secret")
    rabbitmq_vhost: str = os.getenv("RABBITMQ_VHOST", "taskqueue")

    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))

    celery_broker_url: str = os.getenv(
        "CELERY_BROKER_URL",
        "amqp://taskqueue:secret@localhost:5672/taskqueue",
    )
    celery_result_backend: str = os.getenv(
        "CELERY_RESULT_BACKEND",
        "redis://localhost:6379/0",
    )

    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
