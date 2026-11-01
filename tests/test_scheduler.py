"""Unit tests for scheduler.py using an in-memory database and a fake bot."""

import asyncio
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import database  # noqa: E402
import scheduler  # noqa: E402
from telegram.error import TelegramError  # noqa: E402

CHAT = -1001
NOW = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)
TZ = "Asia/Kuala_Lumpur"


class ReminderWindowTests(unittest.TestCase):
    def row(self, due_in_hours):
        return {"due_date": (NOW + timedelta(hours=due_in_hours)).isoformat()}

    def test_deadline_within_24_hours_is_eligible(self):
        self.assertTrue(scheduler.is_in_reminder_window(self.row(12), NOW))

    def test_deadline_exactly_24_hours_away_is_eligible(self):
        self.assertTrue(scheduler.is_in_reminder_window(self.row(24), NOW))

    def test_deadline_more_than_24_hours_away_is_not_eligible(self):
        self.assertFalse(scheduler.is_in_reminder_window(self.row(48), NOW))

    def test_passed_deadline_is_not_eligible(self):
        self.assertFalse(scheduler.is_in_reminder_window(self.row(-1), NOW))


class SendDueRemindersTests(unittest.TestCase):
    def setUp(self):
        self.conn = database.connect(":memory:")
        database.create_schema(self.conn)
        self.bot = MagicMock()
        self.bot.send_message = AsyncMock()

    def tearDown(self):
        self.conn.close()

    def add_task(self, due_in_hours, description="Task", completed=False):
        task_id = database.insert_task(
            self.conn, CHAT, 99, "@adam", 10, description,
            NOW + timedelta(hours=due_in_hours), NOW,
        )
        if completed:
            database.complete_task(self.conn, task_id, CHAT, NOW)
        return task_id

    def run_once(self):
        return asyncio.run(scheduler.send_due_reminders(self.bot, self.conn, NOW, TZ))

    def test_sends_only_eligible_tasks(self):
        eligible = self.add_task(12, "Eligible")
        self.add_task(48, "Too early")
        self.add_task(-1, "Overdue")
        self.add_task(12, "Completed", completed=True)

        self.assertEqual(self.run_once(), 1)
        self.bot.send_message.assert_awaited_once()

        kwargs = self.bot.send_message.await_args.kwargs
        self.assertEqual(kwargs["chat_id"], CHAT)
        self.assertIn("@adam", kwargs["text"])
        self.assertIn("Eligible", kwargs["text"])
        self.assertEqual(database.get_task(self.conn, eligible)["reminder_sent"], 1)

    def test_same_reminder_is_not_sent_twice(self):
        self.add_task(12)
        self.run_once()
        self.assertEqual(self.run_once(), 0)
        self.assertEqual(self.bot.send_message.await_count, 1)

    def test_failed_delivery_is_retried_on_next_run(self):
        task_id = self.add_task(12)
        self.bot.send_message.side_effect = [TelegramError("network down"), None]

        self.assertEqual(self.run_once(), 0)
        self.assertEqual(database.get_task(self.conn, task_id)["reminder_sent"], 0)

        self.assertEqual(self.run_once(), 1)
        self.assertEqual(database.get_task(self.conn, task_id)["reminder_sent"], 1)


class JobRegistrationTests(unittest.TestCase):
    def test_reminder_job_is_registered_on_the_application(self):
        import bot

        conn = database.connect(":memory:")
        database.create_schema(conn)
        application = bot.build_application("123456:FAKE", conn)
        names = [job.name for job in application.job_queue.jobs()]
        self.assertIn("deadline_reminders", names)
        conn.close()


if __name__ == "__main__":
    unittest.main()
