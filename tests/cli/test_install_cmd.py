"""Tests for the install command."""

# Unit under test:
import dem.cli.main as main
import dem.cli.command.install_cmd as install_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

## Global test variables
runner = CliRunner()

@patch("dem.cli.command.install_cmd.stderr.print")
def test_install_dev_env_invalid_name(mock_stderr_print):
    # Test setup
    test_invalid_name = "fake_dev_env_name"

    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = None
    main.platform = mock_platform
        
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["install", test_invalid_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code
    
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_invalid_name)
    mock_stderr_print.assert_called_once_with(f"[red]Error: The {test_invalid_name} Development Environment does not exist.[/]")



@patch("dem.cli.command.install_cmd.stdout.print")
def test_install_dev_env_valid_name(mock_stdout_print):
     # Test setup
    fake_dev_env_to_install = MagicMock()
    fake_dev_env_to_install.name = "dev_env"
    fake_dev_env_to_install.is_installed = False    
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = fake_dev_env_to_install
    main.platform = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["install", fake_dev_env_to_install.name ], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code
    
    mock_platform.get_dev_env_by_name.assert_called_once_with(fake_dev_env_to_install.name )
    mock_platform.install_dev_env.assert_called_once_with(fake_dev_env_to_install)
    mock_stdout_print.assert_called_once_with(f"[green]Successfully installed the {fake_dev_env_to_install.name}![/]")


@patch("dem.cli.command.install_cmd.stderr.print")
def test_install_dev_env_already_installed(mock_stderr_print):
     # Test setup
    fake_dev_env_to_install = MagicMock()
    fake_dev_env_to_install.name = "dev_env"
    fake_dev_env_to_install.is_installed = True
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = fake_dev_env_to_install
    main.platform = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["install", fake_dev_env_to_install.name ], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code    
    
    mock_stderr_print.assert_called_once_with(f"[red]Error: The {fake_dev_env_to_install.name} Development Environment is already installed.[/]")

@patch("dem.cli.command.install_cmd.stderr.print")
def test_install_dev_env_valid_name_failed(mock_stderr_print):
     # Test setup
    fake_dev_env_to_install = MagicMock()
    fake_dev_env_to_install.name = "dev_env"
    fake_dev_env_to_install.is_installed = False   
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = fake_dev_env_to_install
    test_exception_text = "test_exception_text"
    mock_platform.install_dev_env.side_effect = install_cmd.PlatformError(test_exception_text)
    main.platform = mock_platform    

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["install", fake_dev_env_to_install.name ], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code
    
    mock_platform.get_dev_env_by_name.assert_called_once_with(fake_dev_env_to_install.name )
    mock_stderr_print.assert_called_once_with(f"[red]Platform error: {test_exception_text}[/]")

