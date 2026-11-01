"""Handle Telegram commands: parse arguments, call task management, format replies."""

from datetime import datetime, timezone

from telegram import Update
from telegram.ext import ContextTypes

from config import get_timezone
from task_manager import (
    TODO_USAGE,
    ValidationError,
    complete_task,
    create_task,
    format_due_date,
    format_task_lines,
    parse_todo,
)
import database

START_MESSAGE = (
    "Welcome to PingTask!\n\n"
    "I help group members create tasks, track deadlines, and receive reminders.\n\n"
    "Send /help to see the available commands."
)

HELP_MESSAGE = (
    "Available commands:\n\n"
    "/start - Start the bot\n"
    "/help - Show this help message\n"
    "/todo @username Task description by Date/Time - Create a task\n"
    "/tasks - View pending tasks in this group\n"
    "/mytasks - View your pending tasks\n"
    "/done <task ID> - Mark a task as completed"
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply to /start with a welcome message."""
    await update.message.reply_text(START_MESSAGE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply to /help with the list of available commands."""
    await update.message.reply_text(HELP_MESSAGE)


def _connection(context: ContextTypes.DEFAULT_TYPE):
    """Return the database connection stored when the application started."""
    return context.bot_data["db"]


def _assignee_id(update: Update, assignee: str) -> int | None:
    """Find the assignee's Telegram user ID when Telegram can supply it.

    Telegram only gives a user ID when the mention is a "text mention" (chosen
    from the autocomplete list) or when the assignee is the sender.
    """
    for entity in update.message.entities or []:
        if entity.type == "text_mention" and entity.user is not None:
            return entity.user.id

    sender = update.effective_user
    if sender.username and f"@{sender.username}".lower() == assignee.lower():
        return sender.id
    return None


async def todo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create a task from "/todo @username description by Date/Time"."""
    text = " ".join(context.args or [])
    if not text:
        await update.message.reply_text(TODO_USAGE)
        return

    timezone_name = get_timezone()
    now = datetime.now(timezone.utc)
    try:
        new_task = parse_todo(text, now, timezone_name)
    except ValidationError as error:
        await update.message.reply_text(str(error))
        return

    task_id = create_task(
        _connection(context),
        chat_id=update.effective_chat.id,
        creator_id=update.effective_user.id,
        new_task=new_task,
        assignee_id=_assignee_id(update, new_task.assignee),
        now=now,
    )
    due = format_due_date(new_task.due_date, timezone_name)
    await update.message.reply_text(
        f"Task #{task_id} created for {new_task.assignee}: "
        f"{new_task.description} (due {due})"
    )


async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all pending tasks in this group, earliest deadline first."""
    rows = database.get_pending_tasks(_connection(context), update.effective_chat.id)
    if not rows:
        await update.message.reply_text("No pending tasks in this group.")
        return
    await update.message.reply_text(format_task_lines(rows, get_timezone()))


async def mytasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List pending tasks assigned to the sender in this group."""
    sender = update.effective_user
    username = f"@{sender.username}" if sender.username else None
    rows = database.get_personal_tasks(
        _connection(context),
        update.effective_chat.id,
        sender.id,
        username,
    )
    if not rows:
        await update.message.reply_text("You have no pending tasks in this group.")
        return
    await update.message.reply_text(format_task_lines(rows, get_timezone()))


async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mark a task as completed: "/done <task ID>"."""
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Use: /done <task ID>, for example /done 3")
        return

    sender = update.effective_user
    now = datetime.now(timezone.utc)
    try:
        row = complete_task(
            _connection(context),
            chat_id=update.effective_chat.id,
            task_id=int(context.args[0]),
            user_id=sender.id,
            username=sender.username,
            now=now,
        )
    except ValidationError as error:
        await update.message.reply_text(str(error))
        return

    await update.message.reply_text(
        f"Task #{row['id']} marked as completed: {row['task_description']}"
    )
