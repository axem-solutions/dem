"""Unit tests for the del-cat CLI command."""
# tests/cli/test_del_cat_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
@patch("dem.cli.command.del_cat_cmd.stdout.print")
@patch("dem.cli.command.del_cat_cmd.DevEnvLocalSetup")
def test_del_cat(mock_DevEnvLocalSetup: MagicMock, mock_stdout_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_platform
    test_catalog_to_delete = {
        "name":  "test_catalog_name",
        "url": "test_url1"
    }
    test_catalogs = [
        test_catalog_to_delete,
        {
            "name": "test_name2",
            "url": "test_url2"
        },
    ]
    mock_platform.dev_env_catalogs.list_catalog_configs.return_value = test_catalogs

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["del-cat", test_catalog_to_delete["name"]], 
                                  color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_DevEnvLocalSetup.assert_called_once()
    mock_platform.dev_env_catalogs.list_catalog_configs.assert_called_once()
    mock_platform.dev_env_catalogs.delete_catalog.assert_called_once_with(test_catalog_to_delete)
    mock_stdout_print.assert_called_once_with("[green]The input catalog has been successfully deleted.")

@patch("dem.cli.command.del_cat_cmd.stderr.print")
@patch("dem.cli.command.del_cat_cmd.DevEnvLocalSetup")
def test_del_cat_not_exist(mock_DevEnvLocalSetup: MagicMock, mock_stderr_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_platform
    mock_platform.dev_env_catalogs.list_catalog_configs.return_value = []

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["del-cat", "test_name"], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_DevEnvLocalSetup.assert_called_once()
    mock_platform.dev_env_catalogs.list_catalog_configs.assert_called_once()
    mock_stderr_print.assert_called_once_with("[red]Error: The input catalog name doesn't exist![/]")