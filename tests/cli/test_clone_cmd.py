"""Tests for the clone CLI command."""
# tests/cli/test_clone_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.clone_cmd as clone_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.cli.command.clone_cmd.typer.confirm")
@patch("dem.cli.command.clone_cmd.stdout.print")
def test_handle_existing_local_dev_env(mock_stdout_print: MagicMock, mock_typer_confirm: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_local_dev_env = MagicMock()

    # Run unit under test
    clone_cmd.handle_existing_local_dev_env(mock_platform, mock_local_dev_env)

    # Check expectations
    mock_stdout_print.assert_called_once_with("[yellow]The Dev Env already exists. By continuing the local Dev Env will be uninstalled.[/]")
    mock_typer_confirm.assert_called_once_with("Continue with overwrite?", abort=True)
    mock_platform.local_dev_envs.remove.assert_called_once_with(mock_local_dev_env)

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

@patch("dem.cli.command.clone_cmd.handle_existing_local_dev_env")
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
    mock_platform.flush_descriptors.assert_called_once_with()