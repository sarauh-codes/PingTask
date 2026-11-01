"""Background APScheduler job that sends deadline reminders."""

import logging
from datetime import datetime, timedelta, timezone

from telegram.error import TelegramError
from telegram.ext import Application, ContextTypes

import database
from config import get_timezone
from task_manager import format_due_date

REMINDER_INTERVAL = timedelta(minutes=10)
REMINDER_WINDOW = timedelta(hours=24)
FIRST_RUN_DELAY = timedelta(seconds=30)

logger = logging.getLogger(__name__)


def is_in_reminder_window(row, now: datetime) -> bool:
    """Return True if the task's deadline is after now and within the next 24 hours."""
    due_date = datetime.fromisoformat(row["due_date"])
    return now < due_date <= now + REMINDER_WINDOW


def build_reminder_text(row, timezone_name: str) -> str:
    """Create the reminder message for one task."""
    due = format_due_date(row["due_date"], timezone_name)
    return (
        f"Reminder: {row['assignee']}, task #{row['id']} is due {due}: "
        f"{row['task_description']}"
    )


async def send_due_reminders(bot, connection, now: datetime, timezone_name: str) -> int:
    """Send reminders for eligible tasks and return how many were delivered.

    A task is marked as reminded only after Telegram accepts the message.
    If delivery fails, the task stays eligible and is retried on the next run.
    """
    sent = 0
    for row in database.get_tasks_requiring_reminders(connection, now):
        if not is_in_reminder_window(row, now):
            continue
        try:
            await bot.send_message(
                chat_id=row["chat_id"],
                text=build_reminder_text(row, timezone_name),
            )
        except TelegramError as error:
            logger.warning("Could not send reminder for task #%s: %s", row["id"], error)
            continue

        database.mark_reminder_sent(connection, row["id"], row["chat_id"])
        sent += 1
    return sent


async def reminder_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Scheduled job entry point: check for due reminders using the current UTC time."""
    await send_due_reminders(
        context.bot,
        context.bot_data["db"],
        datetime.now(timezone.utc),
        get_timezone(),
    )


def schedule_reminders(application: Application) -> None:
    """Register the reminder check to run every 10 minutes."""
    application.job_queue.run_repeating(
        reminder_job,
        interval=REMINDER_INTERVAL,
        first=FIRST_RUN_DELAY,
        name="deadline_reminders",
    )
