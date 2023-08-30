"""Tests for the load CLI command."""
# tests/cli/test_load_cmd.py

# Unit under test:
from mock import patch
import dem.cli.main as main
import dem.cli.command.load_cmd as load_cmd

# Test framework
import io
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from rich.console import Console
import json

## Global test variables
# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.cli.command.load_cmd.json.load")
@patch("dem.cli.command.load_cmd.open")
def test_load_dev_env_to_dev_env_json_already_exist(mock_open, mock_json):
    # Test setup
    mock_platform = MagicMock()
    fake_opened_file = MagicMock()
    mock_open.return_value = fake_opened_file

    mock_json = MagicMock()

    path="/home/cica.json"

    test_name = "test_name"
    test_dev_env = {
        "name": test_name
    }
    mock_json.return_value = test_dev_env

    mock_platform.get_dev_env_by_name.return_value = MagicMock()
    retval_dev_env_cant_load = load_cmd.load_dev_env_to_dev_env_json(mock_platform,path)  
    
    assert retval_dev_env_cant_load is False

@patch("dem.cli.command.load_cmd.DevEnv")
@patch("dem.cli.command.load_cmd.json.load")
@patch("dem.cli.command.load_cmd.open")
def test_load_dev_env_to_dev_env_json(mock_open, mock_json, mock_DevEnvLocal: MagicMock):
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
    retval_dev_env_load = load_cmd.load_dev_env_to_dev_env_json(mock_platform,path)    
    
    # Check expectations
    assert retval_dev_env_load is True
    mock_open.assert_called_once_with(path, "r")
    mock_platform.get_dev_env_by_name.assert_called()
    mock_DevEnvLocal.assert_called_once_with(test_dev_env)
    mock_new_dev_env.check_image_availability.assert_called_once_with(mock_platform.tool_images)
    mock_platform.pull_images.assert_called_once_with(mock_new_dev_env.tools)
    fake_opened_file.close.assert_called() 

   
@patch("dem.cli.command.load_cmd.open",MagicMock())
@patch("dem.cli.command.load_cmd.json.load")
@patch("dem.cli.command.load_cmd.DevEnvLocalSetup")
def test_json_decode_error(mock_DevEnvLocalSetup,mock_json):
     # Test setup
    fake_local_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_local_platform
    path="/home/cica.json"

    mock_json.side_effect = json.decoder.JSONDecodeError("asd","asd",0)
    fake_local_platform.get_dev_env_by_name.return_value = MagicMock()
    retval_dev_env_cant_load = load_cmd.load_dev_env_to_dev_env_json(fake_local_platform,path)  
    
    assert retval_dev_env_cant_load is False

def test_wo_path():

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["load"])

    # Check expectations
    assert 2 == runner_result.exit_code

def test_with_invalid_file():

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["load", "asd"])

    # Check expectations
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[red]Error: The input file does not exist.[/]")
    assert console.file.getvalue() == runner_result.stderr
    


@patch("dem.cli.command.load_cmd.load_dev_env_to_dev_env_json")
@patch("dem.cli.command.load_cmd.check_is_file_exist")
def test_wrong_execution(mock_file_check,mock_load_dev_env):

    mock_file_check.return_value = True
    mock_load_dev_env.return_value = False
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["load", "asd"])
       
    console = Console(file=io.StringIO())
    console.print("[red]Error: Something went wrong.[/]")
    assert console.file.getvalue() == runner_result.stderr

@patch("dem.cli.command.load_cmd.load_dev_env_to_dev_env_json")
@patch("dem.cli.command.load_cmd.check_is_file_exist")
def test_execution(mock_file_check,mock_load_dev_env):

    mock_file_check.return_value = True
    mock_load_dev_env.return_value = True
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["load", "asd"])
    assert 0 == runner_result.exit_code

def test_check_is_file_exist_param_is_none():
    # Run unit under test
    actual_file_exist = load_cmd.check_is_file_exist(None)

    # Check expectations
    assert actual_file_exist is False