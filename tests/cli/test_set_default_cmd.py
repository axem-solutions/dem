"""Unit tests for the set-default command."""
# tests/cli/execute.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.set_default_cmd as set_default_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.cli.command.set_default_cmd.stdout.print")
def test_execute(mock_stdout_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_dev_env = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env

    # Run unit under test
    set_default_cmd.execute(mock_platform, "fake_dev_env_name")

    # Check expectations
    assert "fake_dev_env_name" is mock_platform.default_dev_env_name

    mock_platform.get_dev_env_by_name.assert_called_once_with("fake_dev_env_name")
    mock_platform.flush_dev_env_properties.assert_called_once()
    mock_stdout_print.assert_called_once_with("[green]The default Development Environment is now set to fake_dev_env_name![/]")

@patch("dem.cli.command.set_default_cmd.stderr.print")
def test_execute_dev_env_not_exist(mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = None

    # Run unit under test
    set_default_cmd.execute(mock_platform, "fake_dev_env_name")

    # Check expectations
    mock_platform.get_dev_env_by_name.assert_called_once_with("fake_dev_env_name")
    mock_stderr_print.assert_called_once_with(f"[red]Error: The fake_dev_env_name Development Environment does not exist.[/]")

@patch("dem.cli.command.set_default_cmd.stdout.print")
@patch("dem.cli.command.set_default_cmd.stderr.print")
def test_execute_not_installed(mock_stderr_print: MagicMock, mock_stdout_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_dev_env = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env
    mock_dev_env.is_installed = False

    # Run unit under test
    set_default_cmd.execute(mock_platform, "fake_dev_env_name")

    # Check expectations
    mock_platform.get_dev_env_by_name.assert_called_once_with("fake_dev_env_name")
    mock_stderr_print.assert_called_once_with(f"[red]Error: The fake_dev_env_name Development Environment is not installed.[/]")
    mock_stdout_print.assert_called_once_with("Only installed Development Environments can be set as default.")

@patch("dem.cli.command.set_default_cmd.execute")
def test_set_default_cmd(mock_execute: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_dev_env_name = "test_dev_env_name"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["set-default", test_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_execute.assert_called_once_with(mock_platform, test_dev_env_name)