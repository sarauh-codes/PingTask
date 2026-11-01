"""Unit tests for task_manager.py."""

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import database  # noqa: E402
import task_manager  # noqa: E402
from task_manager import ValidationError  # noqa: E402

TZ = "Asia/Kuala_Lumpur"
CHAT = -1001
CREATOR = 99
ASSIGNEE = 10
NOW = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)  # 20:00 in Kuala Lumpur


class ParseTodoTests(unittest.TestCase):
    def test_parses_valid_task(self):
        task = task_manager.parse_todo("@adam Finish schema by tomorrow 5pm", NOW, TZ)
        self.assertEqual(task.assignee, "@adam")
        self.assertEqual(task.description, "Finish schema")
        # Tomorrow 5pm in Kuala Lumpur (UTC+8) is 09:00 UTC on 2 Nov 2026.
        self.assertEqual(task.due_date.astimezone(timezone.utc), datetime(2026, 11, 2, 9, 0, tzinfo=timezone.utc))

    def test_uses_last_by_when_description_contains_by(self):
        task = task_manager.parse_todo("@adam Read the step by step guide by tomorrow 5pm", NOW, TZ)
        self.assertEqual(task.description, "Read the step by step guide")

    def test_rejects_missing_assignee(self):
        with self.assertRaisesRegex(ValidationError, "assignee is missing"):
            task_manager.parse_todo("Finish schema by tomorrow 5pm", NOW, TZ)

    def test_rejects_missing_deadline_word(self):
        with self.assertRaisesRegex(ValidationError, "deadline is missing"):
            task_manager.parse_todo("@adam Finish schema", NOW, TZ)

    def test_rejects_empty_description(self):
        with self.assertRaisesRegex(ValidationError, "description is empty"):
            task_manager.parse_todo("@adam by tomorrow 5pm", NOW, TZ)

    def test_rejects_empty_deadline(self):
        with self.assertRaisesRegex(ValidationError, "deadline is empty"):
            task_manager.parse_todo("@adam Finish schema by ", NOW, TZ)

    def test_rejects_unreadable_deadline(self):
        with self.assertRaisesRegex(ValidationError, "could not understand"):
            task_manager.parse_todo("@adam Finish schema by blorp zonk", NOW, TZ)

    def test_rejects_deadline_in_the_past(self):
        with self.assertRaisesRegex(ValidationError, "must be in the future"):
            task_manager.parse_todo("@adam Finish schema by 2020-01-01 10:00", NOW, TZ)


class FormatTests(unittest.TestCase):
    def test_formats_utc_deadline_in_configured_timezone(self):
        self.assertEqual(
            task_manager.format_due_date("2026-11-02T09:00:00+00:00", TZ),
            "02 Nov 2026, 05:00 PM",
        )


class CompleteTaskTests(unittest.TestCase):
    def setUp(self):
        self.conn = database.connect(":memory:")
        database.create_schema(self.conn)
        self.task_id = database.insert_task(
            self.conn, CHAT, CREATOR, "@adam", ASSIGNEE, "Finish schema",
            NOW + timedelta(hours=5), NOW,
        )

    def tearDown(self):
        self.conn.close()

    def test_assignee_can_complete(self):
        row = task_manager.complete_task(self.conn, CHAT, self.task_id, ASSIGNEE, "adam", NOW)
        self.assertEqual(row["status"], "completed")

    def test_creator_can_complete(self):
        row = task_manager.complete_task(self.conn, CHAT, self.task_id, CREATOR, None, NOW)
        self.assertEqual(row["status"], "completed")

    def test_other_user_is_rejected(self):
        with self.assertRaisesRegex(ValidationError, "Only the task's assignee or creator"):
            task_manager.complete_task(self.conn, CHAT, self.task_id, 555, "someone", NOW)

    def test_username_match_works_when_assignee_id_is_unknown(self):
        database.insert_task(
            self.conn, CHAT, CREATOR, "@Maya", None, "No id yet",
            NOW + timedelta(hours=5), NOW,
        )
        row = task_manager.complete_task(self.conn, CHAT, 2, 777, "maya", NOW)
        self.assertEqual(row["status"], "completed")

    def test_task_from_another_group_is_rejected(self):
        with self.assertRaisesRegex(ValidationError, "does not exist in this group"):
            task_manager.complete_task(self.conn, -2002, self.task_id, ASSIGNEE, "adam", NOW)

    def test_missing_task_is_rejected(self):
        with self.assertRaisesRegex(ValidationError, "does not exist"):
            task_manager.complete_task(self.conn, CHAT, 404, ASSIGNEE, "adam", NOW)

    def test_completed_task_is_rejected(self):
        task_manager.complete_task(self.conn, CHAT, self.task_id, ASSIGNEE, "adam", NOW)
        with self.assertRaisesRegex(ValidationError, "already completed"):
            task_manager.complete_task(self.conn, CHAT, self.task_id, ASSIGNEE, "adam", NOW)


if __name__ == "__main__":
    unittest.main()
