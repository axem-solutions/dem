"""Tests for the add_cat CLI command."""
# tests/cli/test_add_cat_cmd.py

# Unit under test:
import dem.cli.main as main
from dem.core.commands import add_cat_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
@patch("dem.core.commands.add_cat_cmd.stdout.print")
def test_add_cat(mock_stdout_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_name = "test_name"
    test_url = "test_url"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["add-cat", test_name, test_url], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.dev_env_catalogs.add_catalog.assert_called_once_with(test_name, test_url)
    mock_stdout_print.assert_called_once_with("[green]The catalog has been successfully added.[/]")

@patch("dem.core.commands.add_cat_cmd.stderr.print")
def test_add_cat_failure(mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_name = "test_name"
    test_url = "test_url"

    test_exception_text = "test_exception_text"
    mock_platform.dev_env_catalogs.add_catalog.side_effect = add_cat_cmd.CatalogError(test_exception_text)

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["add-cat", test_name, test_url], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.dev_env_catalogs.add_catalog.assert_called_once_with(test_name, test_url)
    mock_stderr_print.assert_has_calls([
        call(f"[red]Catalog error: {test_exception_text}[/]\n"),
        call("[red]The catalog could not be added.[/]")
    ])