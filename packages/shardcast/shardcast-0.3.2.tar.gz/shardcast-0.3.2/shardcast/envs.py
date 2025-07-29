"""Constants for the shardcast package."""

from typing import TYPE_CHECKING, Any, List
import os

if TYPE_CHECKING:
    SHARDCAST_SHARD_SIZE: int = 50_000_000
    SHARDCAST_MAX_DISTRIBUTION_FOLDERS: int = 5
    SHARDCAST_HTTP_PORT: int = 8000
    SHARDCAST_RETRY_ATTEMPTS: int = 5
    SHARDCAST_FAST_RETRY_ATTEMPTS: int = 3
    SHARDCAST_FAST_RETRY_INTERVAL: int = 2
    SHARDCAST_SLOW_RETRY_INTERVAL: int = 15
    SHARDCAST_LOG_LEVEL: str = "INFO"
    SHARDCAST_DISTRIBUTION_FILE: str = "distribution.txt"
    SHARDCAST_HTTP_TIMEOUT: int = 30
    SHARDCAST_MAX_CONCURRENT_DOWNLOADS: int = 10
    SHARDCAST_VERSION_PREFIX: str = "v"

_env = {
    "SHARDCAST_SHARD_SIZE": lambda: int(os.getenv("SHARDCAST_SHARD_SIZE", "50000000")),
    "SHARDCAST_MAX_DISTRIBUTION_FOLDERS": lambda: int(os.getenv("SHARDCAST_MAX_DISTRIBUTION_FOLDERS", "5")),
    "SHARDCAST_HTTP_PORT": lambda: int(os.getenv("SHARDCAST_HTTP_PORT", "8000")),
    "SHARDCAST_RETRY_ATTEMPTS": lambda: int(os.getenv("SHARDCAST_RETRY_ATTEMPTS", "5")),
    "SHARDCAST_FAST_RETRY_ATTEMPTS": lambda: int(os.getenv("SHARDCAST_FAST_RETRY_ATTEMPTS", "3")),
    "SHARDCAST_FAST_RETRY_INTERVAL": lambda: int(os.getenv("SHARDCAST_FAST_RETRY_INTERVAL", "2")),
    "SHARDCAST_SLOW_RETRY_INTERVAL": lambda: int(os.getenv("SHARDCAST_SLOW_RETRY_INTERVAL", "15")),
    "SHARDCAST_LOG_LEVEL": lambda: os.getenv("SHARDCAST_LOG_LEVEL", "INFO"),
    "SHARDCAST_DISTRIBUTION_FILE": lambda: os.getenv("SHARDCAST_DISTRIBUTION_FILE", "distribution.txt"),
    "SHARDCAST_HTTP_TIMEOUT": lambda: int(os.getenv("SHARDCAST_HTTP_TIMEOUT", "30")),
    "SHARDCAST_MAX_CONCURRENT_DOWNLOADS": lambda: int(os.getenv("SHARDCAST_MAX_CONCURRENT_DOWNLOADS", "10")),
    "SHARDCAST_VERSION_PREFIX": lambda: os.getenv("SHARDCAST_VERSION_PREFIX", "v"),
}


def __getattr__(name: str) -> Any:
    if name not in _env:
        raise AttributeError(f"Invalid environment variable: {name}")
    return _env[name]()


def __dir__() -> List[str]:
    return list(_env.keys())
