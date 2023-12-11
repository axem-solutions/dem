"""Tests for the add_cat CLI command."""
# tests/cli/test_add_cat_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
def test_add_cat():
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_name = "test_name"
    test_url = "test_url"

    mock_platform.dev_env_catalogs.list_catalog_configs.return_value = []

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["add-cat", test_name, test_url], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.dev_env_catalogs.list_catalog_configs.assert_called_once()
    expected_catalog = {
            "name": test_name,
            "url": test_url
        }
    mock_platform.dev_env_catalogs.add_catalog.assert_called_once_with(expected_catalog)

@patch("dem.cli.command.add_cat_cmd.stdout.print")
def test_add_cat_already_added(mock_stdout_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_name = "test_name"
    test_url = "test_url"

    mock_platform.dev_env_catalogs.list_catalog_configs.return_value = [{
        "name": test_name,
        "url": test_url
    }]

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["add-cat", test_name, test_url], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.dev_env_catalogs.list_catalog_configs.assert_called_once()
    mock_stdout_print.assert_called_once_with("[yellow]The input catalog is already added.[/]")