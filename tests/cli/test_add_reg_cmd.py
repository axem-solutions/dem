"""Tests for the add_reg CLI command."""
# tests/cli/test_add_reg_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
def test_add_reg():
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_name = "test_name"
    test_url = "test_url"

    mock_platform.registries.list_registry_configs.return_value = []

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["add-reg", test_name, test_url], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.registries.list_registry_configs.assert_called_once()
    expected_registry = {
            "name": test_name,
            "url": test_url
        }
    mock_platform.registries.add_registry.assert_called_once_with(expected_registry)

@patch("dem.cli.command.add_reg_cmd.stdout.print")
def test_add_reg_already_added(mock_stdout_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_name = "test_name"
    test_url = "test_url"

    mock_platform.registries.list_registry_configs.return_value = [{
        "name": test_name,
        "url": test_url
    }]

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["add-reg", test_name, test_url], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.registries.list_registry_configs.assert_called_once()
    mock_stdout_print.assert_called_once_with("[yellow]The input registry is already added.[/]")