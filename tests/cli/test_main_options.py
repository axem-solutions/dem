"""Unit tests for running the dem in CLI mode without commands."""
# tests/cli/test_main_options.py

# Unit under test
import dem.cli.main as main

# Test framework
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

import typer

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.cli.main.__app_name__", "axem-dem")
@patch("dem.cli.main.stdout.print")
@patch("dem.cli.main.importlib.metadata.version")
def test_version_as_installed(mock_importlib_metadata_version, mock_stdout_print):
    # Test setup
    test_version = "0.1.2"
    mock_importlib_metadata_version.return_value = test_version

    # Run unit under test
    result = runner.invoke(main.typer_cli, ["--version"])

    # Check expectations
    assert result.exit_code == 0

    mock_stdout_print.assert_called_once_with("[cyan]" + main.__app_name__ + " v" + test_version + "[/]")

@patch("dem.cli.main.stdout.print")
@patch("dem.cli.main.importlib.metadata.version")
def test_version_as_module(mock_importlib_metadata_version, mock_stdout_print):
    # Test setup
    mock_importlib_metadata_version.side_effect = Exception()

    # Run unit under test
    result = runner.invoke(main.typer_cli, ["-v"])

    # Check expectations
    assert result.exit_code == 0