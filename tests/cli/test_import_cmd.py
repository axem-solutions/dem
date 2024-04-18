"""Tests for the import CLI command."""
# tests/cli/test_import_cmd.py

# Unit under test:
from mock import patch
import dem.cli.main as main
import dem.cli.command.import_cmd as import_cmd

# Test framework
import io
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from pytest import raises

from rich.console import Console
import json

## Global test variables
# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.cli.command.import_cmd.stderr.print")
@patch("dem.cli.command.import_cmd.json.load")
@patch("dem.cli.command.import_cmd.open")
def test_import_dev_env_from_json_already_exist(mock_open: MagicMock, mock_json: MagicMock, 
                                                mock_stderr_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    fake_opened_file = MagicMock()
    mock_open.return_value = fake_opened_file

    path="/home/cica.json"

    test_name = "test_name"
    test_dev_env = {
        "name": test_name
    }
    mock_json.return_value = test_dev_env

    mock_platform.get_dev_env_by_name.return_value = MagicMock()

    # Run unit under test
    with raises(import_cmd.typer.Abort):
        import_cmd.import_dev_env_from_json(mock_platform,path)

    # Check expectations
    mock_open.assert_called_once_with(path, "r")
    mock_json.assert_called_once_with(fake_opened_file)
    mock_platform.get_dev_env_by_name.assert_called()
    mock_stderr_print.assert_called_once_with("[red]Error: The Development Environment already exists.[/]")

@patch("dem.cli.command.import_cmd.DevEnv")
@patch("dem.cli.command.import_cmd.json.load")
@patch("dem.cli.command.import_cmd.open")
def test_import_dev_env_from_json(mock_open, mock_json, mock_DevEnvLocal: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    fake_opened_file = MagicMock()
    mock_open.return_value = fake_opened_file

    path="/home/cica.json"

    test_name = "test_name"
    test_dev_env = {
        "name": test_name
    }
    mock_json.return_value = test_dev_env
    mock_platform.get_dev_env_by_name.return_value = None
    mock_new_dev_env = MagicMock()
    mock_DevEnvLocal.return_value = mock_new_dev_env
    mock_new_dev_env.tools = MagicMock()

    # Run unit under test
    import_cmd.import_dev_env_from_json(mock_platform,path)    
    
    # Check expectations
    mock_open.assert_called_once_with(path, "r")
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_name)
    mock_DevEnvLocal.assert_called_once_with(test_dev_env)
    fake_opened_file.close.assert_called() 

@patch("dem.cli.command.import_cmd.open",MagicMock())
@patch("dem.cli.command.import_cmd.json.load")
def test_json_decode_error(mock_json):
     # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform
    path="/home/cica.json"

    mock_json.side_effect = json.decoder.JSONDecodeError("asd","asd",0)
    mock_platform.get_dev_env_by_name.return_value = MagicMock()

    # Run unit under test
    with raises(import_cmd.typer.Abort):
        import_cmd.import_dev_env_from_json(mock_platform,path)

def test_with_invalid_file():
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["import", "asd"])

    # Check expectations
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[red]Error: The input file does not exist.[/]")
    assert console.file.getvalue() == runner_result.stderr

@patch("dem.cli.command.import_cmd.import_dev_env_from_json")
@patch("dem.cli.command.import_cmd.os.path.exists")
def test_execution(mock_os_path_exists: MagicMock, mock_import_dev_env_from_json: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_os_path_exists.return_value = True

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["import", "asd"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_os_path_exists.assert_called_with("asd")
    mock_import_dev_env_from_json.assert_called_once_with(mock_platform, "asd")
    mock_platform.flush_dev_env_properties.assert_called_once()