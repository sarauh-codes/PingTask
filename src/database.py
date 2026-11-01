"""SQLite connection handling, table creation and parameterized queries."""

import sqlite3
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    creator_id INTEGER NOT NULL,
    assignee TEXT NOT NULL,
    assignee_id INTEGER,
    task_description TEXT NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending', 'completed')),
    reminder_sent INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_tasks_chat_status
ON tasks(chat_id, status);

CREATE INDEX IF NOT EXISTS idx_tasks_assignee
ON tasks(chat_id, assignee_id);

CREATE INDEX IF NOT EXISTS idx_tasks_due_date
ON tasks(due_date);
"""


def connect(db_path: str = "pingtask.db") -> sqlite3.Connection:
    """Open a SQLite connection whose rows can be read by column name."""
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def create_schema(connection: sqlite3.Connection) -> None:
    """Create the tasks table and its indexes if they do not exist yet."""
    with connection:
        connection.executescript(SCHEMA)


def to_db_time(value: datetime) -> str:
    """Convert a timezone-aware datetime to a UTC ISO string for storage.

    Storing every timestamp in one fixed format keeps string comparisons in
    SQL (such as "due_date > ?") correct.

    Raises:
        ValueError: If the datetime has no timezone information.
    """
    if value.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware.")
    return value.astimezone(timezone.utc).isoformat(timespec="seconds")


def insert_task(
    connection: sqlite3.Connection,
    chat_id: int,
    creator_id: int,
    assignee: str,
    assignee_id: int | None,
    task_description: str,
    due_date: datetime,
    created_at: datetime,
) -> int:
    """Insert a new pending task and return its ID."""
    with connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (
                chat_id,
                creator_id,
                assignee,
                assignee_id,
                task_description,
                due_date,
                status,
                reminder_sent,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 'pending', 0, ?)
            """,
            (
                chat_id,
                creator_id,
                assignee,
                assignee_id,
                task_description,
                to_db_time(due_date),
                to_db_time(created_at),
            ),
        )
    return cursor.lastrowid


def get_task(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    """Return one task by ID, or None if it does not exist."""
    return connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,),
    ).fetchone()


def get_pending_tasks(connection: sqlite3.Connection, chat_id: int) -> list[sqlite3.Row]:
    """Return pending tasks in one group, earliest deadline first."""
    return connection.execute(
        """
        SELECT *
        FROM tasks
        WHERE chat_id = ?
        AND status = 'pending'
        ORDER BY due_date ASC
        """,
        (chat_id,),
    ).fetchall()


def get_personal_tasks(
    connection: sqlite3.Connection,
    chat_id: int,
    assignee_id: int,
    assignee_username: str | None,
) -> list[sqlite3.Row]:
    """Return pending tasks assigned to one user in one group, earliest deadline first.

    Tasks created with only an @username (no Telegram user ID) are matched by
    username when the task has no assignee_id.
    """
    return connection.execute(
        """
        SELECT *
        FROM tasks
        WHERE chat_id = ?
        AND status = 'pending'
        AND (
            assignee_id = ?
            OR (assignee_id IS NULL AND assignee = ? COLLATE NOCASE)
        )
        ORDER BY due_date ASC
        """,
        (chat_id, assignee_id, assignee_username),
    ).fetchall()


def complete_task(
    connection: sqlite3.Connection,
    task_id: int,
    chat_id: int,
    completed_at: datetime,
) -> bool:
    """Mark a pending task in the given group as completed.

    Returns:
        True if a task was updated, False if no matching pending task exists.

    Authorization is not checked here. The caller must verify that the user
    may complete the task before calling this function.
    """
    with connection:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET status = 'completed',
                completed_at = ?
            WHERE id = ?
            AND chat_id = ?
            AND status = 'pending'
            """,
            (to_db_time(completed_at), task_id, chat_id),
        )
    return cursor.rowcount == 1


def get_tasks_requiring_reminders(
    connection: sqlite3.Connection,
    now: datetime,
) -> list[sqlite3.Row]:
    """Return pending tasks with no reminder sent yet whose deadline is still ahead.

    The 24-hour reminder window is applied by the scheduler in Python.
    """
    return connection.execute(
        """
        SELECT *
        FROM tasks
        WHERE status = 'pending'
        AND reminder_sent = 0
        AND due_date > ?
        ORDER BY due_date ASC
        """,
        (to_db_time(now),),
    ).fetchall()


def mark_reminder_sent(connection: sqlite3.Connection, task_id: int, chat_id: int) -> bool:
    """Record that a reminder was delivered for a task.

    Call this only after the Telegram message was sent successfully.

    Returns:
        True if the reminder flag was set, False if it was already set or the task does not exist.
    """
    with connection:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET reminder_sent = 1
            WHERE id = ?
            AND chat_id = ?
            AND reminder_sent = 0
            """,
            (task_id, chat_id),
        )
    return cursor.rowcount == 1
