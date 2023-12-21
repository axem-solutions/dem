"""Tests for the uninstall command."""


# Unit under test:
import dem.cli.main as main
import dem.cli.command.uninstall_cmd as uninstall_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

import docker.errors

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
    mock_stderr_print.assert_called_once_with("[red]Error: The [bold]" + test_invalid_name + "[/bold] Development Environment doesn't exist.")


@patch("dem.cli.command.uninstall_cmd.stdout.print")
def test_uninstall_dev_env_valid_name(mock_stdout_print):
     # Test setup
    fake_dev_env_to_uninstall = MagicMock()
    fake_dev_env_to_uninstall.name = "dev_env"
    fake_dev_env_to_uninstall.installed = "True"    
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = [fake_dev_env_to_uninstall]
    mock_platform.get_dev_env_status_by_name.return_value = "True"
    main.platform = mock_platform
    mock_platform.try_to_remove_tool_images.return_value = True

            
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["uninstall", fake_dev_env_to_uninstall.name ], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code
    
    mock_platform.get_dev_env_by_name.assert_called_once_with(fake_dev_env_to_uninstall.name )
    mock_stdout_print.assert_called_once_with("[green]Successfully deleted the " + fake_dev_env_to_uninstall.name  + "![/]")


@patch("dem.cli.command.uninstall_cmd.stderr.print")
def test_uninstall_dev_env_valid_name_not_installed(mock_stderr_print):
     # Test setup
    fake_dev_env_to_uninstall = MagicMock()
    fake_dev_env_to_uninstall.name = "dev_env"
    fake_dev_env_to_uninstall.installed = "False"    
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = [fake_dev_env_to_uninstall]
    mock_platform.get_dev_env_status_by_name.return_value = "False"
    main.platform = mock_platform    

        
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["uninstall", fake_dev_env_to_uninstall.name ], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code
    
    mock_platform.get_dev_env_by_name.assert_called_once_with(fake_dev_env_to_uninstall.name )
    mock_stderr_print.assert_called_once_with("[red]Error: The [bold]" + fake_dev_env_to_uninstall.name + "[/bold] Development Environment uninstall failed")


@patch("dem.cli.command.uninstall_cmd.stderr.print")
def test_uninstall_dev_env_valid_name_failed(mock_stderr_print):
     # Test setup
    fake_dev_env_to_uninstall = MagicMock()
    fake_dev_env_to_uninstall.name = "dev_env"
    fake_dev_env_to_uninstall.installed = "True"    
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = [fake_dev_env_to_uninstall]
    mock_platform.get_dev_env_status_by_name.return_value = "True"
    mock_platform.try_to_remove_tool_images.return_value = False
    main.platform = mock_platform    

        
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["uninstall", fake_dev_env_to_uninstall.name ], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code
    
    mock_platform.get_dev_env_by_name.assert_called_once_with(fake_dev_env_to_uninstall.name )
    mock_stderr_print.assert_called_once_with("[red]Error: The [bold]" + fake_dev_env_to_uninstall.name + "[/bold] Development Environment uninstall failed")

