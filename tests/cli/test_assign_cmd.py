"""Tests for the assign command."""
# tests/cli/test_assign_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.core.commands.assign_cmd as assign_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from click.testing import Result

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.core.commands.assign_cmd.os.path.isdir")
@patch("dem.core.commands.assign_cmd.stdout.print")
def test_assign(mock_stdout_print: MagicMock, mock_isdir: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_isdir.return_value = True
    mock_dev_env = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env

    test_dev_env_name = "dev_env_name"
    test_project_path = "test_project_path"

    # Run unit under test
    runner_result: Result = runner.invoke(main.typer_cli, 
                                          ["assign", test_dev_env_name, test_project_path], 
                                          color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_isdir.assert_called_once_with(test_project_path)
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_platform.assign_dev_env.assert_called_once_with(mock_dev_env, test_project_path)
    mock_stdout_print.assert_called_once_with(f"\n[green]Successfully assigned the {test_dev_env_name} Dev Env to the project at {test_project_path}![/]")

@patch("dem.core.commands.assign_cmd.stderr.print")
@patch("dem.core.commands.assign_cmd.os.path.isdir")
def test_assign_invalid_path(mock_isdir: MagicMock, mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()

    mock_isdir.return_value = False

    test_dev_env_name = "dev_env_name"
    test_project_path = "test_project_path"

    # Run unit under test
    assign_cmd.execute(mock_platform, test_dev_env_name, test_project_path)

    # Check expectations
    mock_isdir.assert_called_once_with(test_project_path)
    mock_stderr_print.assert_called_once_with(f"[red]Error: The {test_project_path} path does not exist.[/]")

@patch("dem.core.commands.assign_cmd.stderr.print")
@patch("dem.core.commands.assign_cmd.os.path.isdir")
def test_assign_invalid_dev_env(mock_isdir: MagicMock, mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = None

    mock_isdir.return_value = True

    test_dev_env_name = "dev_env_name"
    test_project_path = "test_project_path"

    # Run unit under test
    assign_cmd.execute(mock_platform, test_dev_env_name, test_project_path)

    # Check expectations
    mock_isdir.assert_called_once_with(test_project_path)
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_stderr_print.assert_called_once_with(f"[red]Error: The {test_dev_env_name} Development Environment does not exist.[/]")