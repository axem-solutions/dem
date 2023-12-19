"""Tests for the uninstall command."""

# Unit under test:
import dem.cli.main as main
import dem.cli.command.uninstall_cmd as uninstall_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

## Global test variables
runner = CliRunner()

@patch("dem.cli.command.uninstall_cmd.stderr.print")
def test_uninstall_dev_env_invalid_name(mock_stderr_print):
    # Test setup
    test_invalid_name = "fake_dev_env_name"

    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = None
    main.platform = mock_platform
        
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["uninstall", test_invalid_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code
    
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_invalid_name)
    mock_stderr_print.assert_called_once_with(f"[red]Error: The {test_invalid_name} Development Environment does not exist.[/]")

@patch("dem.cli.command.uninstall_cmd.stdout.print")
def test_uninstall_dev_env_valid_name(mock_stdout_print):
     # Test setup
    fake_dev_env_to_uninstall = MagicMock()
    fake_dev_env_to_uninstall.name = "dev_env"
    fake_dev_env_to_uninstall.is_installed = "True"    
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = fake_dev_env_to_uninstall
    main.platform = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["uninstall", fake_dev_env_to_uninstall.name ], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code
    
    mock_platform.get_dev_env_by_name.assert_called_once_with(fake_dev_env_to_uninstall.name )
    mock_platform.uninstall_dev_env.assert_called_once_with(fake_dev_env_to_uninstall)
    mock_stdout_print.assert_called_once_with(f"[green]Successfully deleted the {fake_dev_env_to_uninstall.name}![/]")

@patch("dem.cli.command.uninstall_cmd.stderr.print")
def test_uninstall_dev_env_valid_name_not_installed(mock_stderr_print):
     # Test setup
    fake_dev_env_to_uninstall = MagicMock()
    fake_dev_env_to_uninstall.name = "dev_env"
    fake_dev_env_to_uninstall.is_installed = "False"    
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = fake_dev_env_to_uninstall
    main.platform = mock_platform    

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["uninstall", fake_dev_env_to_uninstall.name ], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code
    
    mock_platform.get_dev_env_by_name.assert_called_once_with(fake_dev_env_to_uninstall.name)
    mock_stderr_print.assert_called_once_with(f"[red]Error: The {fake_dev_env_to_uninstall.name} Development Environment is not installed.[/]")

@patch("dem.cli.command.uninstall_cmd.stderr.print")
def test_uninstall_dev_env_valid_name_failed(mock_stderr_print):
     # Test setup
    fake_dev_env_to_uninstall = MagicMock()
    fake_dev_env_to_uninstall.name = "dev_env"
    fake_dev_env_to_uninstall.is_installed = "True"    
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = fake_dev_env_to_uninstall
    test_exception_text = "test_exception_text"
    mock_platform.uninstall_dev_env.side_effect = uninstall_cmd.PlatformError(test_exception_text)
    main.platform = mock_platform    

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["uninstall", fake_dev_env_to_uninstall.name ], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code
    
    mock_platform.get_dev_env_by_name.assert_called_once_with(fake_dev_env_to_uninstall.name )
    mock_stderr_print.assert_called_once_with(f"[red]Error: Platform error: {test_exception_text}[/]")