"""Unit tests for error handling and logging setup in bot.py."""

import asyncio
import logging
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import bot  # noqa: E402
from telegram.error import NetworkError  # noqa: E402


class ErrorHandlerTests(unittest.TestCase):
    def run_handler(self, error):
        context = MagicMock()
        context.error = error
        with patch.object(bot, "logger") as logger:
            asyncio.run(bot.error_handler(None, context))
        return logger

    def test_network_error_is_logged_as_warning_without_traceback(self):
        logger = self.run_handler(NetworkError("httpx.ConnectError"))
        logger.warning.assert_called_once()
        logger.error.assert_not_called()

    def test_unexpected_error_is_logged_with_traceback(self):
        error = RuntimeError("boom")
        logger = self.run_handler(error)
        logger.error.assert_called_once()
        self.assertIs(logger.error.call_args.kwargs["exc_info"], error)


class HttpxLoggingTests(unittest.TestCase):
    def test_httpx_logs_are_not_printed_at_info_level(self):
        # Each Telegram request URL contains the bot token, so INFO logs must stay hidden.
        self.assertGreaterEqual(logging.getLogger("httpx").getEffectiveLevel(), logging.WARNING)


if __name__ == "__main__":
    unittest.main()
