"""Initialize and run the Telegram bot."""

import logging

from telegram.error import NetworkError, TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes

import database
from config import ConfigError, get_bot_token, get_database_path
from handlers import (
    done_command,
    help_command,
    mytasks_command,
    start_command,
    tasks_command,
    todo_command,
)

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# httpx logs every request URL at INFO level, and the URL contains the bot token.
logging.getLogger("httpx").setLevel(logging.WARNING)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors from command handlers without crashing the bot.

    Network errors are usually temporary, so they are logged as warnings
    without a full traceback. Other errors keep their traceback.
    """
    error = context.error
    if isinstance(error, NetworkError):
        logger.warning("Network error while handling an update: %s", error)
    elif isinstance(error, TelegramError):
        logger.warning("Telegram error while handling an update: %s", error)
    else:
        logger.error("Unexpected error while handling an update", exc_info=error)


def build_application(token: str, connection) -> Application:
    """Create the Telegram application, share the database, and register commands."""
    application = Application.builder().token(token).build()
    application.bot_data["db"] = connection
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("todo", todo_command))
    application.add_handler(CommandHandler("tasks", tasks_command))
    application.add_handler(CommandHandler("mytasks", mytasks_command))
    application.add_handler(CommandHandler("done", done_command))
    application.add_error_handler(error_handler)
    return application


def main() -> None:
    """Load configuration, prepare the database, and start polling for Telegram updates."""
    try:
        token = get_bot_token()
    except ConfigError as error:
        logger.error("%s", error)
        raise SystemExit(1) from error

    connection = database.connect(get_database_path())
    database.create_schema(connection)

    logger.info("Starting PingTask bot")
    build_application(token, connection).run_polling()


if __name__ == "__main__":
    main()
