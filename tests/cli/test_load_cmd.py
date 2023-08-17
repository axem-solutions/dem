"""Tests for the load CLI command."""
# tests/cli/test_load_cmd.py

# Unit under test:
from mock import patch
import dem.cli.main as main
import dem.cli.command.load_cmd as load_cmd

# Test framework
import io
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call, PropertyMock
from rich.console import Console

from dem.core.dev_env_setup import DevEnvLocalSetup
import tests.fake_data as fake_data

import json
## Global test variables
# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)


@patch("dem.cli.command.load_cmd.json.load")
@patch("dem.cli.command.load_cmd.open")
@patch("dem.cli.command.load_cmd.DevEnvLocalSetup")
def test_load_dev_env_to_dev_env_json(mock_DevEnvLocalSetup,mock_open,mock_json):
    # Test setup
    fake_local_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_local_platform
    fake_opened_file = MagicMock()
    mock_open.return_value = fake_opened_file

    mock_json = MagicMock()
    #mock_json.read.return_value = json.load(fake_data.dev_env_json)
    #mock_json.deserialized = mock_json.read.return_value    

    path="/home/cica.json"

    test_name = "test_name"
    test_dev_env = {
        "name": test_name
    }
    mock_json.return_value = test_dev_env

    fake_local_platform.get_dev_env_by_name.return_value = MagicMock()
    retval_dev_env_cant_load = load_cmd.load_dev_env_to_dev_env_json(fake_local_platform,path)  
    
    assert retval_dev_env_cant_load is False
    

    fake_local_platform.get_dev_env_by_name.return_value = None
    retval_dev_env_load = load_cmd.load_dev_env_to_dev_env_json(fake_local_platform,path)    
    
    assert retval_dev_env_load is True
    fake_local_platform.get_dev_env_by_name.assert_called()
    fake_local_platform.dev_envs.append.assert_called_once()
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
