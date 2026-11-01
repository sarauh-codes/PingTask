"""Load application settings (bot token, timezone) from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_TIMEZONE = "Asia/Kuala_Lumpur"


class ConfigError(RuntimeError):
    """Raised when required configuration is missing."""


def get_bot_token() -> str:
    """Return the Telegram bot token from the environment.

    Raises:
        ConfigError: If BOT_TOKEN is missing or empty.
    """
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise ConfigError(
            "BOT_TOKEN is not set. Copy .env.example to .env and add your bot token."
        )
    return token


def get_timezone() -> str:
    """Return the configured timezone name, falling back to the default."""
    return os.getenv("TIMEZONE", DEFAULT_TIMEZONE).strip() or DEFAULT_TIMEZONE
