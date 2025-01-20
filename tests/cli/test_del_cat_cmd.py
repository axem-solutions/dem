"""Unit tests for the del-cat CLI command."""
# tests/cli/test_del_cat_cmd.py

# Unit under test:
import dem.cli.main as main
from dem.core.commands import del_cat_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
@patch("dem.core.commands.del_cat_cmd.stdout.print")
def test_del_cat(mock_stdout_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_catalog_to_delete = "test_catalog_to_delete"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["del-cat", test_catalog_to_delete], 
                                          color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.dev_env_catalogs.delete_catalog.assert_called_once_with(test_catalog_to_delete)
    mock_stdout_print.assert_called_once_with(f"[green]The [bold]{test_catalog_to_delete}[/bold] catalog has been successfully deleted.")

@patch("dem.core.commands.del_cat_cmd.stderr.print")
def test_del_cat_failure(mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_catalog_to_delete = "test_catalog_to_delete"
    test_exception_text = "test_exception_text"
    mock_platform.dev_env_catalogs.delete_catalog.side_effect = del_cat_cmd.CatalogError(test_exception_text)

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["del-cat", test_catalog_to_delete], 
                                  color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.dev_env_catalogs.delete_catalog.assert_called_once_with(test_catalog_to_delete)
    mock_stderr_print.assert_has_calls([
        call(f"[red]Catalog error: {test_exception_text}[/]\n"),
        call("[red]The catalog could not be deleted.[/]")
    ])