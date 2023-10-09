"""Tests for the export CLI command."""
# tests/cli/test_export_cmd.py

# Unit under test:
from mock import patch
import dem.cli.main as main
import dem.cli.command.export_cmd as export_cmd

# Test framework
import io
from typer.testing import CliRunner
from unittest.mock import MagicMock
from rich.console import Console

## Global test variables
# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.cli.command.export_cmd.open")
@patch("dem.cli.command.export_cmd.os.path.isdir")
def test_create_exported_dev_env_json(mock_os_path_isdir,mock_open):
    # Test setup
    dev_env_name = "dev_env_name"
    dev_env_json = {
                    "name": "Cica",
                    "tools": [
                        {
                            "type": "build system",
                            "image_name": "axemsolutions/make_gnu_arm",
                            "image_version": "latest"
                        }]
                   }
    given_path = "home"    
    mock_os_path_isdir.return_value = False    
    fake_opened_file = MagicMock()
    mock_open.return_value = fake_opened_file

    # Run unit under test
    export_cmd.create_exported_dev_env_json(dev_env_name,dev_env_json,given_path)
    fake_opened_file.write.assert_called()
    fake_opened_file.close.assert_called()            
    mock_open.assert_called_with(given_path , "w")
    mock_os_path_isdir.assert_called()


    mock_os_path_isdir.return_value = True
    export_cmd.create_exported_dev_env_json(dev_env_name,dev_env_json,given_path)
    fake_opened_file.write.assert_called()
    fake_opened_file.close.assert_called()            
    mock_open.assert_called_with( given_path+"/"+dev_env_name , "w")
    mock_os_path_isdir.assert_called()

    mock_os_path_isdir.return_value = False
    given_path = "/home/axem" 
    export_cmd.create_exported_dev_env_json(dev_env_name,dev_env_json,given_path)
    fake_opened_file.write.assert_called()
    fake_opened_file.close.assert_called()            
    mock_open.assert_called_with( given_path , "w")
    mock_os_path_isdir.assert_called()

    mock_os_path_isdir.return_value = False
    given_path = None 
    export_cmd.create_exported_dev_env_json(dev_env_name,dev_env_json,given_path)
    fake_opened_file.write.assert_called()
    fake_opened_file.close.assert_called()            
    mock_open.assert_called_with( dev_env_name , "w")
    mock_os_path_isdir.assert_called()

def test_wo_path():
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["export", "Cica"])

    # Check expectations
    assert 0 == runner_result.exit_code

def test_with_invalid_devenv():
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["export", ""])

    # Check expectations
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[red]Error: The input Development Environment does not exist.[/]")
    assert console.file.getvalue() == runner_result.stderr
    
@patch("dem.cli.command.export_cmd.create_exported_dev_env_json")
@patch("dem.cli.command.export_cmd.DevEnvLocalSetup")
def test_execute_valid_parameters(mock_DevEnvLocalSetup: MagicMock, 
                                  mock_create_exported_dev_env_json: MagicMock):
    # Test setup
    test_dev_env_name = "test_dev_env_name"
    test_path_to_export = "test_path_to_export"

    mock_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_platform

    mock_dev_env_to_export = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env_to_export

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["export", test_dev_env_name, 
                                                   test_path_to_export])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_DevEnvLocalSetup.assert_called_once()
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_create_exported_dev_env_json.assert_called_once_with(test_dev_env_name, 
                                                              mock_dev_env_to_export.__dict__,
                                                              test_path_to_export)
    
@patch("dem.cli.command.export_cmd.create_exported_dev_env_json", side_effect=FileNotFoundError("FileNotFoundError"))
@patch("dem.cli.command.export_cmd.DevEnvLocalSetup")
def test_execute_FileNotFoundError(mock_DevEnvLocalSetup: MagicMock, 
                                  mock_create_exported_dev_env_json: MagicMock):
    # Test setup
    test_dev_env_name = "test_dev_env_name"
    test_path_to_export = ""

    mock_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_platform

    mock_dev_env_to_export = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env_to_export

    #Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["export", test_dev_env_name, 
                                                   test_path_to_export])
    assert runner_result.exit_code == 0

    console = Console(file=io.StringIO())
    console.print("[red]Error: Invalid input path.[/]")
    assert console.file.getvalue() == runner_result.stderr

    mock_DevEnvLocalSetup.assert_called_once()
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_create_exported_dev_env_json.assert_called_once_with(test_dev_env_name, 
                                                              mock_dev_env_to_export.__dict__,
                                                              test_path_to_export)
    