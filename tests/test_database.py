"""Unit tests for database.py using an in-memory SQLite database."""

import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import database  # noqa: E402

CHAT_A = -1001
CHAT_B = -1002
NOW = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = database.connect(":memory:")
        database.create_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def add_task(self, chat_id=CHAT_A, assignee_id=10, due_in_hours=24, description="Task"):
        return database.insert_task(
            self.conn,
            chat_id=chat_id,
            creator_id=99,
            assignee="@adam",
            assignee_id=assignee_id,
            task_description=description,
            due_date=NOW + timedelta(hours=due_in_hours),
            created_at=NOW,
        )


class SchemaTests(DatabaseTestCase):
    def test_creates_tasks_table_with_expected_columns(self):
        columns = [row["name"] for row in self.conn.execute("PRAGMA table_info(tasks)")]
        self.assertEqual(
            columns,
            [
                "id", "chat_id", "creator_id", "assignee", "assignee_id",
                "task_description", "due_date", "status", "reminder_sent",
                "created_at", "completed_at",
            ],
        )

    def test_create_schema_is_safe_to_run_twice(self):
        database.create_schema(self.conn)
        self.assertEqual(self.add_task(), 1)


class InsertAndGetTests(DatabaseTestCase):
    def test_insert_returns_id_and_stores_pending_task(self):
        task_id = self.add_task(description="Finish schema")
        task = database.get_task(self.conn, task_id)
        self.assertEqual(task["task_description"], "Finish schema")
        self.assertEqual(task["status"], "pending")
        self.assertEqual(task["reminder_sent"], 0)
        self.assertIsNone(task["completed_at"])

    def test_due_date_is_stored_as_utc_string(self):
        local = datetime(2026, 11, 1, 20, 0, tzinfo=timezone(timedelta(hours=8)))
        task_id = database.insert_task(
            self.conn, CHAT_A, 99, "@adam", 10, "Task", local, NOW
        )
        self.assertEqual(database.get_task(self.conn, task_id)["due_date"], "2026-11-01T12:00:00+00:00")

    def test_rejects_naive_datetime(self):
        with self.assertRaises(ValueError):
            database.insert_task(
                self.conn, CHAT_A, 99, "@adam", 10, "Task",
                datetime(2026, 11, 1, 12, 0), NOW,
            )

    def test_get_task_returns_none_for_missing_id(self):
        self.assertIsNone(database.get_task(self.conn, 404))


class PendingTasksTests(DatabaseTestCase):
    def test_returns_only_pending_tasks_for_the_group_sorted_by_deadline(self):
        later = self.add_task(due_in_hours=48, description="later")
        sooner = self.add_task(due_in_hours=2, description="sooner")
        other_group = self.add_task(chat_id=CHAT_B, due_in_hours=1)
        done = self.add_task(due_in_hours=3)
        database.complete_task(self.conn, done, CHAT_A, NOW)

        ids = [row["id"] for row in database.get_pending_tasks(self.conn, CHAT_A)]
        self.assertEqual(ids, [sooner, later])
        self.assertNotIn(other_group, ids)


class PersonalTasksTests(DatabaseTestCase):
    def test_returns_only_the_users_pending_tasks_in_this_group(self):
        mine = self.add_task(assignee_id=10)
        self.add_task(assignee_id=20)
        self.add_task(chat_id=CHAT_B, assignee_id=10)

        ids = [row["id"] for row in database.get_personal_tasks(self.conn, CHAT_A, 10, "@adam")]
        self.assertEqual(ids, [mine])

    def test_matches_username_when_task_has_no_user_id(self):
        task_id = database.insert_task(
            self.conn, CHAT_A, 99, "@Adam", None, "No id yet", NOW + timedelta(hours=5), NOW
        )
        ids = [row["id"] for row in database.get_personal_tasks(self.conn, CHAT_A, 10, "@adam")]
        self.assertEqual(ids, [task_id])


class CompleteTaskTests(DatabaseTestCase):
    def test_completes_pending_task_and_records_time(self):
        task_id = self.add_task()
        self.assertTrue(database.complete_task(self.conn, task_id, CHAT_A, NOW))
        task = database.get_task(self.conn, task_id)
        self.assertEqual(task["status"], "completed")
        self.assertEqual(task["completed_at"], "2026-11-01T12:00:00+00:00")

    def test_rejects_task_from_another_group(self):
        task_id = self.add_task(chat_id=CHAT_A)
        self.assertFalse(database.complete_task(self.conn, task_id, CHAT_B, NOW))
        self.assertEqual(database.get_task(self.conn, task_id)["status"], "pending")

    def test_completing_twice_returns_false_the_second_time(self):
        task_id = self.add_task()
        database.complete_task(self.conn, task_id, CHAT_A, NOW)
        self.assertFalse(database.complete_task(self.conn, task_id, CHAT_A, NOW))

    def test_missing_task_returns_false(self):
        self.assertFalse(database.complete_task(self.conn, 404, CHAT_A, NOW))


class ReminderTests(DatabaseTestCase):
    def test_returns_pending_unreminded_tasks_with_future_deadline(self):
        eligible = self.add_task(due_in_hours=12)
        self.add_task(due_in_hours=-1)  # deadline has passed
        reminded = self.add_task(due_in_hours=12)
        database.mark_reminder_sent(self.conn, reminded, CHAT_A)
        completed = self.add_task(due_in_hours=12)
        database.complete_task(self.conn, completed, CHAT_A, NOW)

        ids = [row["id"] for row in database.get_tasks_requiring_reminders(self.conn, NOW)]
        self.assertEqual(ids, [eligible])

    def test_mark_reminder_sent_only_succeeds_once(self):
        task_id = self.add_task(due_in_hours=12)
        self.assertTrue(database.mark_reminder_sent(self.conn, task_id, CHAT_A))
        self.assertFalse(database.mark_reminder_sent(self.conn, task_id, CHAT_A))
        self.assertEqual(database.get_task(self.conn, task_id)["reminder_sent"], 1)

    def test_mark_reminder_sent_respects_group(self):
        task_id = self.add_task(chat_id=CHAT_A, due_in_hours=12)
        self.assertFalse(database.mark_reminder_sent(self.conn, task_id, CHAT_B))


class PersistenceTests(unittest.TestCase):
    def test_tasks_survive_reconnecting_to_the_same_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / "test.db")

            first = database.connect(path)
            database.create_schema(first)
            task_id = database.insert_task(first, CHAT_A, 99, "@adam", 10, "Persist me", NOW, NOW)
            first.close()

            second = database.connect(path)
            task = database.get_task(second, task_id)
            second.close()
            self.assertEqual(task["task_description"], "Persist me")


if __name__ == "__main__":
    unittest.main()
