"""Handle Telegram commands: parse arguments, call task management, format replies."""

from telegram import Update
from telegram.ext import ContextTypes

START_MESSAGE = (
    "Welcome to PingTask!\n\n"
    "I help group members create tasks, track deadlines, and receive reminders.\n\n"
    "Send /help to see the available commands."
)

HELP_MESSAGE = (
    "Available commands:\n\n"
    "/start - Start the bot\n"
    "/help - Show this help message\n"
    "/todo - Create a task (coming soon)\n"
    "/tasks - View pending tasks (coming soon)\n"
    "/mytasks - View your tasks (coming soon)\n"
    "/done - Mark a task as completed (coming soon)"
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply to /start with a welcome message."""
    await update.message.reply_text(START_MESSAGE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply to /help with the list of available commands."""
    await update.message.reply_text(HELP_MESSAGE)
