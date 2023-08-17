"""Unit tests for the del-reg CLI command."""
# tests/cli/test_del_reg_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
@patch("dem.cli.command.del_reg_cmd.stdout.print")
@patch("dem.cli.command.del_reg_cmd.DevEnvLocalSetup")
def test_del_reg(mock_DevEnvLocalSetup: MagicMock, mock_stdout_print: MagicMock):
    # Test setup
    mock_local_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_local_platform
    test_registry_to_delete = {
        "name":  "test_registry_name",
        "url": "test_url1"
    }
    test_registries = [
        test_registry_to_delete,
        {
            "name": "test_name2",
            "url": "test_url2"
        },
    ]
    mock_local_platform.registries.list_registries.return_value = test_registries

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["del-reg", test_registry_to_delete["name"]], 
                                  color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_DevEnvLocalSetup.assert_called_once()
    mock_local_platform.registries.list_registries.assert_called_once()
    mock_local_platform.registries.delete_registry.assert_called_once_with(test_registry_to_delete)
    mock_stdout_print.assert_called_once_with("[green]The input registry has been successfully deleted.")

@patch("dem.cli.command.del_reg_cmd.stderr.print")
@patch("dem.cli.command.del_reg_cmd.DevEnvLocalSetup")
def test_del_reg_not_exist(mock_DevEnvLocalSetup: MagicMock, mock_stderr_print: MagicMock):
    # Test setup
    mock_local_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_local_platform
    mock_local_platform.registries.list_registries.return_value = []

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["del-reg", "test_name"], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_DevEnvLocalSetup.assert_called_once()
    mock_local_platform.registries.list_registries.assert_called_once()
    mock_stderr_print.assert_called_once_with("[red]Error: The input registry name doesn't exist![/]")