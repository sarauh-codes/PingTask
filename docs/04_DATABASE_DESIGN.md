# PingTask – Database Design

## 1. Database Overview

PingTask uses SQLite as its database management system.

SQLite is suitable for the initial implementation because it is lightweight, requires minimal configuration, and is included in Python's standard library.

Database filename:

`pingtask.db`

## 2. Database Table: tasks

The initial implementation uses one main table named `tasks`.

### 2.1 Table Structure

| Column | Data Type | Constraint | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique task identifier |
| chat_id | INTEGER | NOT NULL | Telegram group chat ID |
| creator_id | INTEGER | NOT NULL | Telegram user ID of the task creator |
| assignee | TEXT | NOT NULL | Telegram username or display name |
| assignee_id | INTEGER | NULL | Telegram user ID of the assignee |
| task_description | TEXT | NOT NULL | Task details |
| due_date | TEXT | NOT NULL | Task deadline in UTC |
| status | TEXT | NOT NULL | pending or completed |
| reminder_sent | INTEGER | DEFAULT 0 | Reminder delivery status |
| created_at | TEXT | NOT NULL | Task creation timestamp |
| completed_at | TEXT | NULL | Task completion timestamp |

## 3. SQL Table Creation

```sql
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
```

## 4. Database Relationships

The initial version does not require multiple tables.

Each task is associated with one Telegram group through its `chat_id`.

A Telegram group can contain multiple tasks, while each task belongs to one group.

Each task also records the creator and assigned user through their Telegram user IDs where available.

## 5. Example Records

| id | chat_id | assignee | task_description | status | reminder_sent |
|---|---|---|---|---|---|
| 1 | -10012345 | @adam | Finish database schema | pending | 0 |
| 2 | -10012345 | @sarah | Prepare presentation slides | pending | 1 |
| 3 | -10012345 | @john | Complete testing | completed | 0 |

The example records are illustrative only.

## 6. Important Database Queries

### 6.1 Insert a New Task

```sql
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
VALUES (?, ?, ?, ?, ?, ?, 'pending', 0, ?);
```

### 6.2 Retrieve Pending Tasks

```sql
SELECT *
FROM tasks
WHERE chat_id = ?
AND status = 'pending'
ORDER BY due_date ASC;
```

### 6.3 Retrieve Personal Tasks

```sql
SELECT *
FROM tasks
WHERE chat_id = ?
AND assignee_id = ?
AND status = 'pending'
ORDER BY due_date ASC;
```

The implementation also matches tasks by username when `assignee_id` is empty:

```sql
AND (
    assignee_id = ?
    OR (assignee_id IS NULL AND assignee = ? COLLATE NOCASE)
)
```

This is needed because Telegram does not give a bot the user ID for a plain `@username`. The ID is stored only when the assignee is picked from Telegram's mention list or is the person creating the task.

### 6.4 Mark a Task as Completed

```sql
UPDATE tasks
SET status = 'completed',
    completed_at = ?
WHERE id = ?
AND chat_id = ?
AND status = 'pending';
```

The application must verify that the user is authorized to complete the task before executing this update.

### 6.5 Retrieve Tasks Requiring Reminders

```sql
SELECT *
FROM tasks
WHERE status = 'pending'
AND reminder_sent = 0
AND due_date > ?;
```

The application will compare the returned deadlines with the configured 24-hour reminder window using Python.

### 6.6 Update Reminder Status

```sql
UPDATE tasks
SET reminder_sent = 1
WHERE id = ?
AND chat_id = ?
AND reminder_sent = 0;
```

## 7. Database Indexes

Indexes can improve the performance of frequently used queries.

```sql
CREATE INDEX IF NOT EXISTS idx_tasks_chat_status
ON tasks(chat_id, status);

CREATE INDEX IF NOT EXISTS idx_tasks_assignee
ON tasks(chat_id, assignee_id);

CREATE INDEX IF NOT EXISTS idx_tasks_due_date
ON tasks(due_date);
```

## 8. Database Considerations

- Use parameterized SQL queries.
- Store timestamps in a consistent UTC format.
- Use Telegram user IDs to identify users whenever possible.
- Use Telegram group IDs to isolate tasks between groups.
- Commit database changes appropriately.
- Mark reminders as sent only after successful Telegram delivery.
- Use transactions when multiple related database operations are required.

## 9. Future Database Expansion

If PingTask becomes more advanced, additional tables may be introduced.

### users

Stores Telegram user information.

### groups

Stores Telegram group information and configuration.

### task_history

Tracks task updates and completion history.

### reminder_logs

Stores reminder delivery attempts and timestamps.

These tables are not required for the initial implementation.