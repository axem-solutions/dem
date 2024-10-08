"""Tests for the run CLI command."""
# tests/cli/test_run_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.run_cmd as run_cmd

# Test framework
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

import typer

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases

@patch("dem.cli.command.run_cmd.typer.confirm")
@patch("dem.cli.command.run_cmd.stdout.print")
@patch("dem.cli.command.run_cmd.stderr.print")
def test_dev_env_health_check(mock_stderr_print: MagicMock, mock_stdout_print: MagicMock, 
                              mock_typer_confirm: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_platform.local_only = False
    mock_dev_env = MagicMock()
    mock_dev_env.name = "my-dev-env"

    mock_dev_env.is_installation_correct.return_value = False

    # Run
    run_cmd.dev_env_health_check(mock_platform, mock_dev_env)

    # Check
    mock_dev_env.assign_tool_image_instances.assert_called_with(mock_platform.tool_images)
    mock_dev_env.is_installation_correct.assert_called()
    mock_stderr_print.assert_called_once_with("[red]Error: Incorrect installation![/]")
    mock_typer_confirm.assert_called_once_with("Should DEM reinstall the DevEnv?", abort=True)
    mock_platform.install_dev_env.assert_called_once_with(mock_dev_env)
    mock_stdout_print.assert_called_once_with(f"[green]DEM successfully fixed the {mock_dev_env.name} Development Environment![/]")

@patch("dem.cli.command.run_cmd.subprocess.run")
@patch("dem.cli.command.run_cmd.dev_env_health_check")
@patch("dem.cli.command.run_cmd.stdout.print")
@patch("dem.cli.command.run_cmd.stderr.print")
def test_run_cmd(mock_stderr_print: MagicMock, mock_stdout_print: MagicMock, 
                 mock_dev_env_health_check: MagicMock, mock_subprocess_run: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_dev_env = MagicMock()
    mock_dev_env.is_installed = True
    mock_dev_env.tasks = {
        "my-task": "echo 'Hello, World!'"
    }
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env

    # Run
    result = runner.invoke(main.typer_cli, ["run", "my-dev-env", "my-task"])

    # Check
    assert result.exit_code == 0

    mock_platform.get_dev_env_by_name.assert_called_once_with("my-dev-env")
    mock_dev_env_health_check.assert_called_once_with(mock_platform, mock_dev_env)
    mock_stdout_print.assert_has_calls([
        call("[green]Running task [bold]my-task[/bold] in Development Environment [bold]my-dev-env[/bold]...[/]\n"),
        call("")
    ])
    mock_subprocess_run.assert_called_once_with("echo 'Hello, World!'", shell=True)

@patch("dem.cli.command.run_cmd.execute")
def test_run_without_dev_env_name(mock_execute: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    # Run
    result = runner.invoke(main.typer_cli, ["run", "my-task"])

    # Check
    assert result.exit_code == 0

    mock_execute.assert_called_once_with(mock_platform, "", "my-task")

@patch("dem.cli.command.run_cmd.subprocess.run")
@patch("dem.cli.command.run_cmd.dev_env_health_check")
@patch("dem.cli.command.run_cmd.stdout.print")
@patch("dem.cli.command.run_cmd.stderr.print")
def test_run_cmd_default_dev_env(mock_stderr_print: MagicMock, mock_stdout_print: MagicMock, 
                                 mock_dev_env_health_check: MagicMock, mock_subprocess_run: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_dev_env = MagicMock()
    mock_dev_env.is_installed = True
    mock_dev_env.tasks = {
        "my-task": "echo 'Hello, World!'"
    }
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env
    test_default_dev_env_name = "my-default-dev-env"
    mock_platform.default_dev_env_name = test_default_dev_env_name

    # Run
    run_cmd.execute(mock_platform, "", "my-task")

    # Check
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_default_dev_env_name)
    mock_dev_env_health_check.assert_called_once_with(mock_platform, mock_dev_env)
    mock_stdout_print.assert_has_calls([
        call(f"[green]Running task [bold]my-task[/bold] in Development Environment [bold]{test_default_dev_env_name}[/bold]...[/]\n"),
        call("")
    ])
    mock_subprocess_run.assert_called_once_with("echo 'Hello, World!'", shell=True)

@patch("dem.cli.command.run_cmd.stderr.print")
def test_run_cmd_no_dev_env_name_no_default(mock_stderr_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_platform.default_dev_env_name = ""
    main.platform = mock_platform

    # Run
    run_cmd.execute(mock_platform, "", "my-task")

    # Check
    mock_stderr_print.assert_called_once_with("[red]Error: Only one parameter is supplied but no default Dev Env is set! Please specify the Dev Env to run the task in or set a default one![/]")

@patch("dem.cli.command.run_cmd.stderr.print")
def test_run_cmd_dev_env_not_found(mock_stderr_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    main.platform = mock_platform
    mock_platform.get_dev_env_by_name.return_value = None

    # Run
    run_cmd.execute(mock_platform, "my-dev-env", "my-task")

    # Check
    mock_stderr_print.assert_called_once_with("[red]Error: Unknown Development Environment: my-dev-env[/]")

@patch("dem.cli.command.run_cmd.stderr.print")
def test_run_cmd_dev_env_not_installed(mock_stderr_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_dev_env = MagicMock()
    mock_dev_env.is_installed = False
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env

    # Run
    run_cmd.execute(mock_platform, "my-dev-env", "my-task")

    # Check
    mock_stderr_print.assert_called_once_with("[red]Error: Development Environment [bold]my-dev-env[/bold] is not installed![/]")

@patch("dem.cli.command.run_cmd.dev_env_health_check")
@patch("dem.cli.command.run_cmd.stderr.print")
def test_run_cmd_task_not_found(mock_stderr_print: MagicMock, 
                                mock_dev_env_health_check: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_dev_env = MagicMock()
    mock_dev_env.is_installed = True
    mock_dev_env.tasks = {}
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env

    # Run
    run_cmd.execute(mock_platform, "my-dev-env", "my-task")

    # Check
    mock_dev_env_health_check.assert_called_once_with(mock_platform, mock_dev_env)
    mock_stderr_print.assert_called_once_with("[red]Error: Task [bold]my-task[/bold] not found in Development Environment [bold]my-dev-env[/bold]![/]")