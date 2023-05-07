"""Settings module."""
from functools import lru_cache

from pydantic import BaseSettings


@lru_cache()
def get_settings():
    return Settings()


class LogConfig(BaseSettings):
    """Logging config."""

    LOGGER_NAME: str = "proj"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {"()": "uvicorn.logging.DefaultFormatter", "fmt": LOG_FORMAT, "datefmt": "%Y-%m-%d %H:%M:%S"},
    }
    handlers = {
        "default": {"formatter": "default", "class": "logging.StreamHandler", "stream": "ext://sys.stderr"},
    }
    loggers = {
        "proj": {"handlers": ["default"], "level": LOG_LEVEL},
    }


class Settings(BaseSettings):
    """Settings."""

    debug: bool
    sentry_dsn: str = ''
    port: int = 8000
    database_url: str
    secret_key: str
    inner_host: str = 'test_proj'
    log_config = LogConfig()

    class Config:
        """Config."""

        env_file = '.env.example'

