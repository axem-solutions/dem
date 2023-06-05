"""Tests for core callback."""
# tests/cli/test_core_cb.py

# Unit under test:
import dem.cli.core_cb as core_cb

# Test framework
from unittest.mock import patch

@patch("dem.cli.core_cb.typer.confirm")
@patch("dem.cli.core_cb.stdout.print")
def test_core_cb(mock_stdout_print, mock_confirm):
    # Test setup
    test_msg = "test_msg"
    test_user_confirm = "test_user_confirm"

    # Run unit under test
    core_cb.user_confirm_cb(msg=test_msg, user_confirm=test_user_confirm)

    # Check expectations
    mock_stdout_print.assert_called_once_with(test_msg)
    mock_confirm.assert_called_once_with(test_user_confirm, abort=True)