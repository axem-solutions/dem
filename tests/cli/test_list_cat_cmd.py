"""Tests for the list_cat CLI command."""
# tests/cli/test_list_cat_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
@patch("dem.cli.command.list_cat_cmd.Table")
@patch("dem.cli.command.list_cat_cmd.stdout.print")
def test_list_cat(mock_stdout_print: MagicMock, mock_Table: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform
    test_catalog_configs = [
        {
            "name": "test_name1",
            "url": "test_url1"
        },
        {
            "name": "test_name2",
            "url": "test_url2"
        },
    ]
    mock_platform.dev_env_catalogs.list_catalog_configs.return_value = test_catalog_configs
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list-cat"], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_Table.assert_called_once()
    calls = [call("name"), call("url")]
    mock_table.add_column.assert_has_calls(calls)

    mock_platform.dev_env_catalogs.list_catalog_configs.assert_called_once()
    
    calls = []
    for catalog_config in test_catalog_configs:
        calls.append(call(catalog_config["name"], catalog_config["url"]))
    mock_table.add_row.assert_has_calls(calls)

    mock_stdout_print.assert_called_once_with(mock_table)

@patch("dem.cli.command.list_cat_cmd.Table")
@patch("dem.cli.command.list_cat_cmd.stdout.print")
def test_list_cat_non_available(mock_stdout_print: MagicMock, mock_Table):
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform
    mock_platform.dev_env_catalogs.list_catalog_configs.return_value = []
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list-cat"], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_Table.assert_called_once()
    calls = [call("name"), call("url")]
    mock_table.add_column.assert_has_calls(calls)

    mock_platform.dev_env_catalogs.list_catalog_configs.assert_called_once()
    
    mock_stdout_print.assert_called_once_with("[yellow]No Development Environment Catalogs are available![/]")