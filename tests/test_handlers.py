"""Unit tests for the /start and /help command handlers."""

import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import handlers  # noqa: E402


def make_update():
    """Build a minimal stand-in for a Telegram Update with a reply method."""
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    return update


class StartCommandTests(unittest.TestCase):
    def test_replies_with_welcome_message(self):
        update = make_update()
        asyncio.run(handlers.start_command(update, MagicMock()))
        update.message.reply_text.assert_awaited_once_with(handlers.START_MESSAGE)


class HelpCommandTests(unittest.TestCase):
    def test_replies_with_help_message(self):
        update = make_update()
        asyncio.run(handlers.help_command(update, MagicMock()))
        update.message.reply_text.assert_awaited_once_with(handlers.HELP_MESSAGE)

    def test_help_lists_all_planned_commands(self):
        for command in ("/start", "/help", "/todo", "/tasks", "/mytasks", "/done"):
            self.assertIn(command, handlers.HELP_MESSAGE)


if __name__ == "__main__":
    unittest.main()
