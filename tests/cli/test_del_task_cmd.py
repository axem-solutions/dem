"""Unit tests for the del-task CLI command."""
# tests/cli/test_del_task_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.core.commands.del_task_cmd as del_task_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

def test_del_task_cmd() -> None:
    # Setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_dev_env = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env

    # Run
    result = runner.invoke(main.typer_cli, ["del-task", "my-dev-env", "my-task"])

    # Check
    assert result.exit_code == 0

    mock_platform.get_dev_env_by_name.assert_called_once_with("my-dev-env")
    mock_dev_env.del_task.assert_called_once_with("my-task")
    mock_platform.flush_dev_env_properties.assert_called_once()

@patch("dem.core.commands.del_task_cmd.stderr")
def test_del_task_cmd_dev_env_not_found(mock_stderr: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_platform.get_dev_env_by_name.return_value = None

    # Run
    result = runner.invoke(main.typer_cli, ["del-task", "my-dev-env", "my-task"])

    # Check
    assert result.exit_code == 0

    mock_platform.get_dev_env_by_name.assert_called_once_with("my-dev-env")
    mock_stderr.print.assert_called_once_with("[red]Error: Development Environment 'my-dev-env' not found![/]")

@patch("dem.core.commands.del_task_cmd.stderr")
def test_del_task_cmd_task_not_found(mock_stderr: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_dev_env = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env
    mock_dev_env.del_task.side_effect = KeyError("Task [bold]my-task[/] not found.")

    # Run
    result = runner.invoke(main.typer_cli, ["del-task", "my-dev-env", "my-task"])

    # Check
    assert result.exit_code == 0

    mock_platform.get_dev_env_by_name.assert_called_once_with("my-dev-env")
    mock_dev_env.del_task.assert_called_once_with("my-task")
    mock_stderr.print.assert_called_once_with("[red] Error: \'Task [bold]my-task[/] not found.\'[/]")