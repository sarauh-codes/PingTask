"""Initialize and run the Telegram bot."""

import logging

from telegram.ext import Application, CommandHandler

from config import ConfigError, get_bot_token
from handlers import help_command, start_command

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_application(token: str) -> Application:
    """Create the Telegram application and register command handlers."""
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    return application


def main() -> None:
    """Load configuration and start polling for Telegram updates."""
    try:
        token = get_bot_token()
    except ConfigError as error:
        logger.error("%s", error)
        raise SystemExit(1) from error

    logger.info("Starting PingTask bot")
    build_application(token).run_polling()


if __name__ == "__main__":
    main()
