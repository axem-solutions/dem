"""Tests for the delete command."""
# tests/cli/test_modify_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.delete_cmd as delete_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

## Global test variables
runner = CliRunner()

@patch("dem.cli.command.delete_cmd.typer.confirm")
@patch("dem.cli.command.delete_cmd.stdout.print")
def test_delete(mock_stdout_print: MagicMock, mock_config: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_dev_env_name = "test_dev_env_name"
    test_dev_env = MagicMock()
    test_dev_env.is_installed = True
    mock_platform.get_dev_env_by_name.return_value = test_dev_env
    mock_platform.local_dev_envs = [test_dev_env]

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["delete", test_dev_env_name])

    # Check expectations
    assert runner_result.exit_code == 0
    assert test_dev_env not in mock_platform.local_dev_envs

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_config.assert_called_once_with("The Development Environment is installed. Do you want to uninstall it?", 
                                        abort=True)
    mock_platform.uninstall_dev_env.assert_called_once_with(test_dev_env)
    mock_stdout_print.assert_has_calls([
        call("Deleting the Development Environment..."),
        call(f"[green]Successfully deleted the {test_dev_env_name}![/]")
    ])
    mock_platform.flush_descriptors.assert_called_once()

@patch("dem.cli.command.delete_cmd.typer.confirm")
@patch("dem.cli.command.delete_cmd.stderr.print")
def test_delete_uninstall_failed(mock_stderr_print: MagicMock, mock_confirm: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_dev_env_name = "test_dev_env_name"
    test_dev_env = MagicMock()
    test_dev_env.is_installed = True
    mock_platform.get_dev_env_by_name.return_value = test_dev_env
    test_exception_text = "test_exception_text" 
    mock_platform.uninstall_dev_env.side_effect = delete_cmd.PlatformError(test_exception_text)

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["delete", test_dev_env_name])

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_confirm.assert_called_once_with("The Development Environment is installed. Do you want to uninstall it?", 
                                        abort=True)
    mock_platform.uninstall_dev_env.assert_called_once_with(test_dev_env)
    mock_stderr_print.assert_called_once_with(f"[red]Platform error: {test_exception_text}[/]")

@patch("dem.cli.command.delete_cmd.stderr.print")
def test_delete_not_existing(mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_dev_env_name = "test_dev_env_name"
    mock_platform.get_dev_env_by_name.return_value = None

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["delete", test_dev_env_name])

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_stderr_print.assert_called_once_with(f"[red]Error: The [bold]{test_dev_env_name}[/bold] Development Environment doesn't exist.")