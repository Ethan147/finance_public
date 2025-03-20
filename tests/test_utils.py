import datetime
import subprocess
import unittest
from typing import Dict, OrderedDict
from unittest.mock import patch

import pandas as pd
from colorama import Fore

from utils import utils


class TestFunctions(unittest.TestCase):

    def test_is_float(self) -> None:
        # Test valid float strings
        self.assertTrue(utils.is_float("3.14"))
        self.assertTrue(utils.is_float("-10.5"))
        self.assertTrue(utils.is_float("0"))

        # Test invalid float strings
        self.assertFalse(utils.is_float("abc"))
        self.assertFalse(utils.is_float("3.14.15"))
        self.assertFalse(utils.is_float(""))

    def test_timestamp(self) -> None:
        result = utils.timestamp()
        self.assertIsInstance(result, str)
        # Ensure format is correct (e.g., "YYYY-MM-DD HH:MM:SS")
        self.assertEqual(len(result), 19)

    @patch("builtins.print")
    def test_print_status(self, mock_print) -> None:
        try:
            utils.print_status("Test status message")
            mock_print.assert_called()
        except Exception as e:
            self.fail(f"print_status() raised {e}")

    @patch("builtins.print")
    def test_print_error(self, mock_print) -> None:
        try:
            utils.print_error("Test error message")
            mock_print.assert_called()
        except Exception as e:
            self.fail(f"print_error() raised {e}")

    def test_open_file_dne(self) -> None:
        try:
            open("dummy_file.ods")
        except FileNotFoundError:
            pass  # Expected since "dummy_file.ods" doesn't exist
        except Exception as e:
            self.fail(f"open() raised {e}")
