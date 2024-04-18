"""Tests for the assign command."""
# tests/cli/test_assign_cmd.py

# Unit under test:
import dem.cli.command.init_cmd as init_cmd

# Test framework
from unittest.mock import MagicMock, patch, call

@patch("dem.cli.command.init_cmd.os.path.isdir")
@patch("dem.cli.command.init_cmd.stdout.print")
@patch("dem.cli.command.init_cmd.typer.confirm")
@patch("dem.cli.command.init_cmd.DevEnv")
def test_execute(mock_DevEnv, mock_confirm, mock_stdout_print, mock_isdir) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_project_path = "/path/to/project"
    mock_dev_env_name = "test_dev_env"
    mock_dev_env = MagicMock()
    mock_dev_env.name = mock_dev_env_name
    mock_DevEnv.return_value = mock_dev_env
    mock_isdir.return_value = True
    mock_platform.local_dev_envs = []

    # Run unit under test
    init_cmd.execute(mock_platform, mock_project_path)

    # Check expectations
    assert mock_dev_env in mock_platform.local_dev_envs

    mock_isdir.assert_called_once_with(mock_project_path)
    mock_DevEnv.assert_called_once_with(descriptor_path=f"{mock_project_path}/.axem/dev_env_descriptor.json")
    mock_confirm.assert_not_called()
    mock_platform.uninstall_dev_env.assert_not_called()
    mock_platform.flush_dev_env_properties.assert_called_once()
    mock_stdout_print.assert_has_calls([call(f"[green]Successfully initialized the {mock_dev_env_name} Dev Env for the project at {mock_project_path}![/]"),
                                        call(f"\nNow you can install the Dev Env with the `dem install {mock_dev_env_name}` command.")])

@patch("dem.cli.command.init_cmd.os.path.isdir")
@patch("dem.cli.command.init_cmd.stderr.print")
def test_execute_project_path_not_existing(mock_stderr_print, mock_isdir) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_project_path = "/path/to/project"
    mock_isdir.return_value = False

    # Run unit under test
    init_cmd.execute(mock_platform, mock_project_path)

    # Check expectations
    mock_isdir.assert_called_once_with(mock_project_path)
    mock_stderr_print.assert_called_once_with(f"[red]Error: The {mock_project_path} path does not exist.[/]")

@patch("dem.cli.command.init_cmd.os.path.isdir")
@patch("dem.cli.command.init_cmd.stderr.print")
@patch("dem.cli.command.init_cmd.DevEnv")
def test_execute_missing_descriptor(mock_DevEnv, mock_stderr_print, mock_isdir) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_project_path = "/path/to/project"
    mock_DevEnv.side_effect = FileNotFoundError
    mock_isdir.return_value = True

    # Run unit under test
    init_cmd.execute(mock_platform, mock_project_path)

    # Check expectations
    mock_isdir.assert_called_once_with(mock_project_path)
    mock_DevEnv.assert_called_once_with(descriptor_path=f"{mock_project_path}/.axem/dev_env_descriptor.json")
    mock_stderr_print.assert_called_once_with("[red]Error: No Dev Env is assigned to this project. You can assign one with `dem assign`.")

@patch("dem.cli.command.init_cmd.os.path.isdir")
@patch("dem.cli.command.init_cmd.stdout.print")
@patch("dem.cli.command.init_cmd.typer.confirm")
@patch("dem.cli.command.init_cmd.DevEnv")
def test_execute_reinit_installed(mock_DevEnv, mock_confirm, mock_stdout_print, mock_isdir) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_project_path = "/path/to/project"
    mock_dev_env_name = "test_dev_env"
    mock_dev_env = MagicMock()
    mock_dev_env.name = mock_dev_env_name
    mock_DevEnv.return_value = mock_dev_env
    mock_isdir.return_value = True
    mock_local_dev_env = MagicMock()
    mock_local_dev_env.name = mock_dev_env_name
    mock_local_dev_env.is_installed = True
    mock_platform.local_dev_envs = [mock_local_dev_env]

    # Run unit under test
    init_cmd.execute(mock_platform, mock_project_path)

    # Check expectations
    assert mock_dev_env in mock_platform.local_dev_envs
    assert mock_local_dev_env not in mock_platform.local_dev_envs

    mock_isdir.assert_called_once_with(mock_project_path)
    mock_DevEnv.assert_called_once_with(descriptor_path=f"{mock_project_path}/.axem/dev_env_descriptor.json")
    mock_confirm.assert_has_calls([call("Would you like to re-init the Dev Env? All local changes will be lost!", abort=True),
                                   call("The Development Environment is installed, so it can't be deleted. Do you want to uninstall it first?", abort=True)])
    mock_platform.uninstall_dev_env.assert_called_once_with(mock_local_dev_env)
    mock_platform.flush_dev_env_properties.assert_called_once()
    mock_stdout_print.assert_has_calls([call(f"[green]Successfully initialized the {mock_dev_env_name} Dev Env for the project at {mock_project_path}![/]"),
                                        call(f"\nNow you can install the Dev Env with the `dem install {mock_dev_env_name}` command.")])

@patch("dem.cli.command.init_cmd.os.path.isdir")
@patch("dem.cli.command.init_cmd.stderr.print")
@patch("dem.cli.command.init_cmd.typer.confirm")
@patch("dem.cli.command.init_cmd.DevEnv")
def test_execute_reinit_installed_uninstall_fails(mock_DevEnv, mock_confirm, mock_stderr_print, 
                                                  mock_isdir) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_project_path = "/path/to/project"
    mock_dev_env_name = "test_dev_env"
    mock_dev_env = MagicMock()
    mock_dev_env.name = mock_dev_env_name
    mock_DevEnv.return_value = mock_dev_env
    mock_isdir.return_value = True
    mock_local_dev_env = MagicMock()
    mock_local_dev_env.name = mock_dev_env_name
    mock_local_dev_env.is_installed = True
    mock_platform.local_dev_envs = [mock_local_dev_env]
    test_exception_text = "test_exception_text"
    mock_platform.uninstall_dev_env.side_effect = init_cmd.PlatformError(test_exception_text)

    # Run unit under test
    init_cmd.execute(mock_platform, mock_project_path)

    # Check expectations
    mock_isdir.assert_called_once_with(mock_project_path)
    mock_DevEnv.assert_called_once_with(descriptor_path=f"{mock_project_path}/.axem/dev_env_descriptor.json")
    mock_confirm.assert_has_calls([call("Would you like to re-init the Dev Env? All local changes will be lost!", abort=True),
                                   call("The Development Environment is installed, so it can't be deleted. Do you want to uninstall it first?", abort=True)])
    mock_platform.uninstall_dev_env.assert_called_once_with(mock_local_dev_env)
    mock_stderr_print.assert_called_once_with(f"[red]Platform error: {test_exception_text}[/]")