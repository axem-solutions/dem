"""Unit tests for the add-task CLI command."""
# tests/cli/test_add_task_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.core.commands.add_task_cmd as add_task_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.core.commands.add_task_cmd.stdout.print")
def test_add_task_cmd(mock_stdout_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_dev_env = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env

    # Run
    result = runner.invoke(main.typer_cli, ["add-task", "my-dev-env", "my-task", "my-command"])

    # Check
    assert result.exit_code == 0

    mock_platform.get_dev_env_by_name.assert_called_once_with("my-dev-env")
    mock_dev_env.add_task.assert_called_once_with("my-task", "my-command")
    mock_platform.flush_dev_env_properties.assert_called_once()
    mock_stdout_print.assert_called_once_with("[green]Task [bold]my-task[/bold] added to Development Environment [bold]my-dev-env[/bold]![/]")

@patch("dem.core.commands.add_task_cmd.stderr.print")
def test_execute_dev_env_not_found(mock_stderr_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = None
    
    test_dev_env_name = "my-dev-env"
    test_task_name = "my-task"
    test_command = "my-command"

    # Run
    add_task_cmd.execute(mock_platform, test_dev_env_name, test_task_name, test_command)

    # Check
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_stderr_print.assert_called_once_with(f"[red]Error: Development Environment '{test_dev_env_name}' not found![/]")