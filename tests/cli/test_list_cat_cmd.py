"""Tests for the list_cat CLI command."""
# tests/cli/test_list_cat_cmd.py

# Unit under test:
import dem.cli.main as main
from dem.cli.command import list_cat_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
@patch("dem.cli.command.list_cat_cmd.Table")
@patch("dem.cli.command.list_cat_cmd.stdout.print")
def test_list_cat(mock_stdout_print: MagicMock, mock_Table: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform
    mock_catalog_1 = MagicMock()
    mock_catalog_1.name = "test_catalog_1"
    mock_catalog_1.url = "test_url_1"
    mock_catalog_2 = MagicMock()
    mock_catalog_2.name = "test_catalog_2"
    mock_catalog_2.url = "test_url_2"
    test_catalog_configs = [
        mock_catalog_1,
        mock_catalog_2
    ]
    mock_platform.dev_env_catalogs.catalogs = test_catalog_configs
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list-cat"], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_Table.assert_called_once()
    calls = [call("name"), call("url")]
    mock_table.add_column.assert_has_calls(calls)
    mock_catalog_1.request_dev_envs.assert_called_once()
    mock_catalog_2.request_dev_envs.assert_called_once()

    calls = [
        call(mock_catalog_1.name, mock_catalog_1.url),
        call(mock_catalog_2.name, mock_catalog_2.url)
    ]
    mock_table.add_row.assert_has_calls(calls)
    mock_stdout_print.assert_called_once_with(mock_table)

@patch("dem.cli.command.list_cat_cmd.Table")
@patch("dem.cli.command.list_cat_cmd.stdout.print")
def test_list_cat_non_available(mock_stdout_print: MagicMock, mock_Table) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform
    mock_platform.dev_env_catalogs.catalogs = []
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list-cat"], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_Table.assert_called_once()
    calls = [call("name"), call("url")]
    mock_table.add_column.assert_has_calls(calls)

    mock_stdout_print.assert_called_once_with("[yellow]No Development Environment Catalogs are available![/]")

@patch("dem.cli.command.list_cat_cmd.Table")
@patch("dem.cli.command.list_cat_cmd.stderr.print")
def test_list_cat_failure(mock_stderr_print: MagicMock, mock_Table: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_table = MagicMock()
    mock_Table.return_value = mock_table
    mock_corrupted_catalog = MagicMock()
    test_exception_text = "test_exception_text"
    mock_corrupted_catalog.request_dev_envs.side_effect = list_cat_cmd.CatalogError(test_exception_text)
    mock_platform.dev_env_catalogs.catalogs = [mock_corrupted_catalog]

    # Run unit under test
    list_cat_cmd.execute(mock_platform)

    # Check expectations
    mock_Table.assert_called_once
    mock_table.add_column.assert_has_calls([call("name"), call("url")])
    mock_corrupted_catalog.request_dev_envs.assert_called_once()
    mock_stderr_print.assert_called_once_with(f"[red]Catalog error: {test_exception_text}[/]")