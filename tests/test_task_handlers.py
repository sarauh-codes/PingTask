"""Unit tests for the /todo, /tasks, /mytasks and /done handlers.

These use an in-memory database and mocked Telegram objects, so no network
calls are made.
"""

import asyncio
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import database  # noqa: E402
import handlers  # noqa: E402

CHAT = -1001


def make_update(text_user_id=10, username="adam", entities=None):
    """Build a minimal stand-in for a Telegram Update sent in CHAT."""
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.entities = entities or []
    update.effective_chat = SimpleNamespace(id=CHAT)
    update.effective_user = SimpleNamespace(id=text_user_id, username=username)
    return update


def make_context(connection, args=None):
    context = MagicMock()
    context.bot_data = {"db": connection}
    context.args = args or []
    return context


def reply_text(update):
    return update.message.reply_text.await_args.args[0]


class HandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = database.connect(":memory:")
        database.create_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def run_command(self, command, update, context):
        asyncio.run(command(update, context))


class TodoCommandTests(HandlerTestCase):
    def test_creates_task_and_confirms(self):
        update = make_update(text_user_id=99, username="sarah")
        context = make_context(self.conn, ["@sarah", "Write", "report", "by", "tomorrow", "5pm"])
        self.run_command(handlers.todo_command, update, context)

        self.assertIn("Task #1 created for @sarah", reply_text(update))
        self.assertEqual(database.get_task(self.conn, 1)["task_description"], "Write report")

    def test_sender_is_recorded_as_assignee_when_mentioning_self(self):
        update = make_update(text_user_id=10, username="adam")
        context = make_context(self.conn, ["@adam", "Fix", "bug", "by", "tomorrow", "5pm"])
        self.run_command(handlers.todo_command, update, context)

        self.assertEqual(database.get_task(self.conn, 1)["assignee_id"], 10)

    def test_text_mention_provides_assignee_id(self):
        mentioned = SimpleNamespace(id=20)
        entity = SimpleNamespace(type="text_mention", user=mentioned)
        update = make_update(text_user_id=99, username="sarah", entities=[entity])
        context = make_context(self.conn, ["@maya", "Draft", "slides", "by", "tomorrow", "5pm"])
        self.run_command(handlers.todo_command, update, context)

        self.assertEqual(database.get_task(self.conn, 1)["assignee_id"], 20)

    def test_no_arguments_shows_usage(self):
        update = make_update()
        self.run_command(handlers.todo_command, update, make_context(self.conn, []))
        self.assertIn("Use: /todo", reply_text(update))

    def test_invalid_input_shows_error_and_stores_nothing(self):
        update = make_update()
        context = make_context(self.conn, ["Finish", "schema"])
        self.run_command(handlers.todo_command, update, context)

        self.assertIn("assignee is missing", reply_text(update))
        self.assertEqual(database.get_pending_tasks(self.conn, CHAT), [])


class ListCommandTests(HandlerTestCase):
    def setUp(self):
        super().setUp()
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        database.insert_task(self.conn, CHAT, 99, "@adam", 10, "Schema", now + timedelta(days=1), now)
        database.insert_task(self.conn, CHAT, 99, "@sarah", 20, "Slides", now + timedelta(days=2), now)

    def test_tasks_lists_all_pending_tasks(self):
        update = make_update()
        self.run_command(handlers.tasks_command, update, make_context(self.conn))
        text = reply_text(update)
        self.assertIn("Schema", text)
        self.assertIn("Slides", text)

    def test_mytasks_lists_only_the_sender_tasks(self):
        update = make_update(text_user_id=10, username="adam")
        self.run_command(handlers.mytasks_command, update, make_context(self.conn))
        text = reply_text(update)
        self.assertIn("Schema", text)
        self.assertNotIn("Slides", text)

    def test_mytasks_empty_message(self):
        update = make_update(text_user_id=555, username="nobody")
        self.run_command(handlers.mytasks_command, update, make_context(self.conn))
        self.assertIn("no pending tasks", reply_text(update))


class DoneCommandTests(HandlerTestCase):
    def setUp(self):
        super().setUp()
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        database.insert_task(self.conn, CHAT, 99, "@adam", 10, "Schema", now + timedelta(days=1), now)

    def test_assignee_completes_task(self):
        update = make_update(text_user_id=10, username="adam")
        self.run_command(handlers.done_command, update, make_context(self.conn, ["1"]))
        self.assertIn("marked as completed", reply_text(update))
        self.assertEqual(database.get_task(self.conn, 1)["status"], "completed")

    def test_other_user_is_rejected(self):
        update = make_update(text_user_id=555, username="stranger")
        self.run_command(handlers.done_command, update, make_context(self.conn, ["1"]))
        self.assertIn("Only the task's assignee or creator", reply_text(update))
        self.assertEqual(database.get_task(self.conn, 1)["status"], "pending")

    def test_non_numeric_id_shows_usage(self):
        update = make_update()
        self.run_command(handlers.done_command, update, make_context(self.conn, ["abc"]))
        self.assertIn("Use: /done", reply_text(update))


if __name__ == "__main__":
    unittest.main()
