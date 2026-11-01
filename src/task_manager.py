"""Task business logic: parse input, validate, create, list and complete tasks."""

import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import dateparser

import database

USERNAME_PATTERN = re.compile(r"^@(\w+)\s+(.+)$", re.DOTALL)
BY_PATTERN = re.compile(r"(?:^|\s)by(?=\s|$)", re.IGNORECASE)

TODO_USAGE = "Use: /todo @username Task description by Date/Time"


class ValidationError(ValueError):
    """Invalid user input. The message is safe to show to the user."""


@dataclass(frozen=True)
class NewTask:
    """A validated task request from the /todo command."""

    assignee: str  # Stored with the leading "@", for example "@adam"
    description: str
    due_date: datetime  # Timezone-aware


def parse_todo(text: str, now: datetime, timezone_name: str) -> NewTask:
    """Parse and validate the text that follows /todo.

    Expected format: "@username Task description by Date/Time".

    Raises:
        ValidationError: If any part is missing, the deadline cannot be read,
            or the deadline is not in the future.
    """
    match = USERNAME_PATTERN.match(text.strip())
    if not match:
        raise ValidationError(f"The assignee is missing. {TODO_USAGE}")

    username = match.group(1)
    rest = match.group(2).strip()

    # Use the last standalone "by" so descriptions may contain "by" themselves.
    separators = list(BY_PATTERN.finditer(rest))
    if not separators:
        raise ValidationError(f"The deadline is missing. Add 'by' and a date/time. {TODO_USAGE}")

    last = separators[-1]
    description = rest[: last.start()].strip()
    deadline_text = rest[last.end() :].strip()
    if not description:
        raise ValidationError(f"The task description is empty. {TODO_USAGE}")
    if not deadline_text:
        raise ValidationError(f"The deadline is empty. {TODO_USAGE}")

    due_date = dateparser.parse(
        deadline_text,
        settings={
            "TIMEZONE": timezone_name,
            "TO_TIMEZONE": "UTC",
            "RETURN_AS_TIMEZONE_AWARE": True,
            "PREFER_DATES_FROM": "future",
            "RELATIVE_BASE": now.astimezone(ZoneInfo(timezone_name)).replace(tzinfo=None),
        },
    )
    if due_date is None:
        raise ValidationError(
            f"I could not understand the deadline '{deadline_text}'. "
            "Try something like 'tomorrow 5pm' or '2026-12-01 17:00'."
        )
    if due_date <= now:
        raise ValidationError("The deadline must be in the future.")

    return NewTask(assignee=f"@{username}", description=description, due_date=due_date)


def format_due_date(value: str | datetime, timezone_name: str) -> str:
    """Format a stored UTC deadline for display in the configured timezone."""
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.astimezone(ZoneInfo(timezone_name)).strftime("%d %b %Y, %I:%M %p")


def format_task_lines(rows: list[sqlite3.Row], timezone_name: str) -> str:
    """Render tasks as numbered lines for a Telegram reply."""
    lines = []
    for row in rows:
        due = format_due_date(row["due_date"], timezone_name)
        lines.append(f"#{row['id']} {row['assignee']}: {row['task_description']} (due {due})")
    return "\n".join(lines)


def create_task(
    connection: sqlite3.Connection,
    chat_id: int,
    creator_id: int,
    new_task: NewTask,
    assignee_id: int | None,
    now: datetime,
) -> int:
    """Store a validated task and return its ID."""
    return database.insert_task(
        connection,
        chat_id=chat_id,
        creator_id=creator_id,
        assignee=new_task.assignee,
        assignee_id=assignee_id,
        task_description=new_task.description,
        due_date=new_task.due_date,
        created_at=now,
    )


def can_complete(row: sqlite3.Row, user_id: int, username: str | None) -> bool:
    """Return True if the user created the task or is its assignee."""
    if user_id in (row["creator_id"], row["assignee_id"]):
        return True
    return username is not None and row["assignee"].lower() == f"@{username}".lower()


def complete_task(
    connection: sqlite3.Connection,
    chat_id: int,
    task_id: int,
    user_id: int,
    username: str | None,
    now: datetime,
) -> sqlite3.Row:
    """Complete a task after checking that it exists, is pending, and the user may complete it.

    Returns:
        The completed task row.

    Raises:
        ValidationError: With a user-facing message if the task cannot be completed.
    """
    row = database.get_task(connection, task_id)
    if row is None or row["chat_id"] != chat_id:
        raise ValidationError(f"Task #{task_id} does not exist in this group.")
    if row["status"] == "completed":
        raise ValidationError(f"Task #{task_id} is already completed.")
    if not can_complete(row, user_id, username):
        raise ValidationError("Only the task's assignee or creator can complete this task.")

    database.complete_task(connection, task_id, chat_id, now)
    return database.get_task(connection, task_id)
