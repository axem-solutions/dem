"""Tests for the clone CLI command."""
# tests/cli/test_clone_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.core.commands.clone_cmd as clone_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call
import pytest

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.core.commands.clone_cmd.typer.confirm")
@patch("dem.core.commands.clone_cmd.stdout.print")
def test_handle_existing_local_dev_env(mock_stdout_print: MagicMock, mock_typer_confirm: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_local_dev_env = MagicMock()

    test_uninstall_dev_env_status = ["test_uninstall_dev_env_status", 
                                     "test_uninstall_dev_env_status2"]
    mock_platform.uninstall_dev_env.return_value = test_uninstall_dev_env_status

    # Run unit under test
    clone_cmd.handle_existing_local_dev_env(mock_platform, mock_local_dev_env)

    # Check expectations
    mock_stdout_print.assert_has_calls([call("[yellow]The Dev Env already exists.[/]"),
                                        call(test_uninstall_dev_env_status[0]),
                                        call(test_uninstall_dev_env_status[1])])
    mock_typer_confirm.assert_has_calls([call("Continue with overwrite?", abort=True),
                                         call("The Dev Env to overwrite is installed. Do you want to uninstall it?", 
                                              abort=True)])
    mock_platform.uninstall_dev_env.assert_called_once_with(mock_local_dev_env)
    mock_platform.local_dev_envs.remove.assert_called_once_with(mock_local_dev_env)

@patch("dem.core.commands.clone_cmd.stderr.print")
@patch("dem.core.commands.clone_cmd.typer.confirm")
@patch("dem.core.commands.clone_cmd.stdout.print")
def test_handle_existing_local_dev_env_PlatformError(mock_stdout_print: MagicMock, 
                                                     mock_typer_confirm: MagicMock,
                                                     mock_stderr_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_local_dev_env = MagicMock()

    test_exception_message = "test_exception_message"
    mock_platform.uninstall_dev_env.side_effect = clone_cmd.PlatformError(test_exception_message)

    # Run unit under test
    with pytest.raises(clone_cmd.typer.Abort):
        clone_cmd.handle_existing_local_dev_env(mock_platform, mock_local_dev_env)

    # Check expectations
    mock_stdout_print.assert_called_once_with("[yellow]The Dev Env already exists.[/]")
    mock_typer_confirm.assert_has_calls([call("Continue with overwrite?", abort=True),
                                         call("The Dev Env to overwrite is installed. Do you want to uninstall it?", 
                                              abort=True)])
    mock_platform.uninstall_dev_env.assert_called_once_with(mock_local_dev_env)
    mock_stderr_print.assert_called_once_with(f"[red]Platform error: {test_exception_message}[/]")
    mock_platform.local_dev_envs.remove.assert_not_called()

def test_execute_no_catalogs() -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_platform.dev_env_catalogs.catalogs = []

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["clone", "not existing env"], color=True)

    # Check expectations
    assert runner_result.exit_code == 0
    assert "Error: No Development Environment Catalogs are available to clone from!" in runner_result.stderr

def test_execute_dev_env_not_available_in_catalog() -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_catalog = MagicMock()
    mock_catalog.get_dev_env_by_name.return_value = None
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]

    test_dev_env_name = "not existing env"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["clone", test_dev_env_name], color=True)

    # Check expectations
    assert runner_result.exit_code == 0
    assert "Error: The input Development Environment is not available." in runner_result.stderr

    mock_catalog.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)

@patch("dem.core.commands.clone_cmd.handle_existing_local_dev_env")
def test_execute_success(mock_handle_existing_local_dev_env: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_catalog = MagicMock()
    mock_catalog_dev_env = MagicMock()
    mock_catalog.get_dev_env_by_name.return_value = mock_catalog_dev_env
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]
    mock_local_dev_env = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_local_dev_env

    test_dev_env_name = "test"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["clone", test_dev_env_name], color=True)

    # Check expectations
    assert runner_result.exit_code == 0
    assert "The Dev Env successfully cloned." in runner_result.stdout

    mock_catalog.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_handle_existing_local_dev_env.assert_called_once_with(mock_platform, mock_local_dev_env)
    mock_platform.local_dev_envs.append.assert_called_once_with(mock_catalog_dev_env)
    mock_platform.flush_dev_env_properties.assert_called_once_with()