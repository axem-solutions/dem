"""Tests for the export CLI command."""
# tests/cli/test_export_cmd.py

# Unit under test:
from mock import patch
import dem.cli.main as main
import dem.core.commands.export_cmd as export_cmd

# Test framework
import io
from typer.testing import CliRunner
from unittest.mock import MagicMock
from rich.console import Console

## Global test variables
# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.core.commands.export_cmd.os.path.isdir")
def test_export_path_is_dir(mock_isdir: MagicMock):
    # Test setup
    test_export_path = "fake_export_path"
    mock_isdir.return_value = True

    mock_dev_env = MagicMock()
    mock_dev_env.name = "fake_dev_env"

    # Run unit under test
    export_cmd.export(mock_dev_env, test_export_path)

    # Check expectations
    mock_isdir.assert_called_once_with(test_export_path)
    mock_dev_env.export.assert_called_once_with(f"{test_export_path}/{mock_dev_env.name}.json")

@patch("dem.core.commands.export_cmd.os.path.isdir")
def test_export_path_is_file(mock_isdir: MagicMock):
    # Test setup
    test_export_path = "fake_export_path.json"
    mock_isdir.return_value = False

    mock_dev_env = MagicMock()
    mock_dev_env.name = "fake_dev_env"

    # Run unit under test
    export_cmd.export(mock_dev_env, test_export_path)

    # Check expectations
    mock_isdir.assert_called_once_with(test_export_path)
    mock_dev_env.export.assert_called_once_with(test_export_path)

@patch("dem.core.commands.export_cmd.os.path.isdir")
def test_export_path_is_empty(mock_isdir: MagicMock):
    # Test setup
    test_export_path = ""
    mock_dev_env = MagicMock()
    mock_dev_env.name = "fake_dev_env"

    mock_isdir.return_value = False

    # Run unit under test
    export_cmd.export(mock_dev_env, test_export_path)

    # Check expectations
    mock_dev_env.export.assert_called_once_with(f"{mock_dev_env.name}.json")

@patch("dem.core.commands.export_cmd.export")
def test_execute(mock_export: MagicMock):
    # Test setup
    test_dev_env_name = "fake_dev_env_name"
    test_export_path = "fake_export_path"

    mock_platform = MagicMock()
    mock_dev_env = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env
    main.platform = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["export", test_dev_env_name, test_export_path], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_export.assert_called_once_with(mock_dev_env, test_export_path)

@patch("dem.core.commands.export_cmd.stderr.print")
def test_execute_dev_env_not_found(mock_stderr_print: MagicMock):
    # Test setup
    test_dev_env_name = "fake_dev_env_name"
    test_export_path = "fake_export_path"

    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = None
    main.platform = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["export", test_dev_env_name, test_export_path], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_stderr_print.assert_called_once_with("[red]Error: The input Development Environment does not exist.[/]")

@patch("dem.core.commands.export_cmd.stderr.print")
@patch("dem.core.commands.export_cmd.export")
def test_execute_invalid_path(mock_export: MagicMock, mock_stderr_print: MagicMock):
    # Test setup
    test_dev_env_name = "fake_dev_env_name"
    test_export_path = "fake_export_path"

    mock_platform = MagicMock()
    mock_dev_env = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env
    main.platform = mock_platform

    mock_export.side_effect = FileNotFoundError

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["export", test_dev_env_name, test_export_path], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_export.assert_called_once_with(mock_dev_env, test_export_path)
    mock_stderr_print.assert_called_once_with("[red]Error: Invalid input path.[/]")