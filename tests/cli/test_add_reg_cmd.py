"""Tests for the add_reg CLI command."""
# tests/cli/test_add_reg_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.add_reg_cmd as add_reg_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
@patch("dem.cli.command.add_reg_cmd.stdout.print")
def test_add_reg(mock_stdout_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_name = "test_name"
    test_url = "test_url"
    test_namespace = "test_namespace"

    mock_platform.registries.list_registry_configs.return_value = []

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["add-reg", test_name, test_url, test_namespace], 
                                  color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.registries.list_registry_configs.assert_called_once()
    expected_registry = {
            "name": test_name,
            "namespace": test_namespace,
            "url": test_url
        }
    mock_platform.registries.add_registry.assert_called_once_with(expected_registry)
    mock_stdout_print.assert_called_once_with(f"[green]The {test_name} registry has been successfully added![/]")

@patch("dem.cli.command.add_reg_cmd.stderr.print")
def test_add_reg_name_taken(mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_name = "test_name"
    test_url = "test_url"
    test_namespace = "test_namespace"

    mock_platform.registries.list_registry_configs.return_value = [{
        "name": test_name,
        "namespace": test_namespace,
        "url": test_url
    }]

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["add-reg", test_name, test_url, test_namespace], 
                                  color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.registries.list_registry_configs.assert_called_once()
    mock_stderr_print.assert_called_once_with("[red]Error: The input registry name is already in use![/]")

@patch("dem.cli.command.add_reg_cmd.stderr.print")
def test_add_reg_registry_error(mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_name = "test_name"
    test_url = "test_url"
    test_namespace = "test_namespace"

    mock_platform.registries.list_registry_configs.return_value = []

    mock_platform.registries.add_registry.side_effect = add_reg_cmd.RegistryError("test_error")

    # Run unit under test
    add_reg_cmd.execute(mock_platform, test_name, test_url, test_namespace)

    # Check expectations
    mock_platform.registries.list_registry_configs.assert_called_once()
    mock_platform.registries.add_registry.assert_called_once()
    mock_stderr_print.assert_called_once_with("[red]Error: Registry error: test_error[/]")