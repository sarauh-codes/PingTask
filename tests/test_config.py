"""Unit tests for config.py."""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import config  # noqa: E402


class GetBotTokenTests(unittest.TestCase):
    def test_returns_token_from_environment(self):
        with patch.dict(os.environ, {"BOT_TOKEN": "123:abc"}):
            self.assertEqual(config.get_bot_token(), "123:abc")

    def test_raises_when_token_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(config.ConfigError):
                config.get_bot_token()

    def test_raises_when_token_blank(self):
        with patch.dict(os.environ, {"BOT_TOKEN": "   "}):
            with self.assertRaises(config.ConfigError):
                config.get_bot_token()


class GetTimezoneTests(unittest.TestCase):
    def test_returns_configured_timezone(self):
        with patch.dict(os.environ, {"TIMEZONE": "Europe/London"}):
            self.assertEqual(config.get_timezone(), "Europe/London")

    def test_falls_back_to_default_when_unset(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(config.get_timezone(), config.DEFAULT_TIMEZONE)

    def test_falls_back_to_default_when_blank(self):
        with patch.dict(os.environ, {"TIMEZONE": ""}):
            self.assertEqual(config.get_timezone(), config.DEFAULT_TIMEZONE)


if __name__ == "__main__":
    unittest.main()
