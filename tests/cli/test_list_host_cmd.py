"""Tests for the list_host CLI command."""
# tests/cli/test_list_host_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
@patch("dem.cli.command.list_host_cmd.Table")
@patch("dem.cli.command.list_host_cmd.stdout.print")
@patch("dem.cli.command.list_host_cmd.DevEnvLocalSetup")
def test_list_host(mock_DevEnvLocalSetup: MagicMock, mock_stdout_print: MagicMock, 
                  mock_Table: MagicMock):
    print("I am running !1")
    # Test setup
    mock_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_platform
    test_hosts = [
        {
            "name": "test_name1",
            "address": "test_url1"
        },
        {
            "name": "test_name2",
            "address": "test_url2"
        },
    ]
    mock_platform.config_file.deserialize["hosts"].return_value = test_hosts
    '''
    return valus should be :
    deserialized  {'registries': [{'name': 'axemsolutions', 'url': 'https://registry.hub.docker.com'}], 'catalogs': [{'name': 'axem', 'url': 'https://axemsolutions.io/dem/dev_env_org.json'}], 'hosts': [{'name': 'Test1', 'address': '129.0.0.1'}, {'name': 'Test2', 'address': '256.256.256.256:9999'}, {'name': 'Test3', 'address': '0.0.0.0'}, {'name': 'Test4', 'address': 'www.axemsolutions.io/dem-doc'}, {'name': 'test5', 'address': '12.12.12.00'}]}
    deserialized.get()  [{'name': 'Test1', 'address': '129.0.0.1'}, {'name': 'Test2', 'address': '256.256.256.256:9999'}, {'name': 'Test3', 'address': '0.0.0.0'}, {'name': 'Test4', 'address': 'www.axemsolutions.io/dem-doc'}, {'name': 'test5', 'address': '12.12.12.00'}]
    deserialized[hosts]  [{'name': 'Test1', 'address': '129.0.0.1'}, {'name': 'Test2', 'address': '256.256.256.256:9999'}, {'name': 'Test3', 'address': '0.0.0.0'}, {'name': 'Test4', 'address': 'www.axemsolutions.io/dem-doc'}, {'name': 'test5', 'address': '12.12.12.00'}]
    '''
    print("deserialized ::::", mock_platform.config_file.deserialize["hosts"])
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list-host"], color=True)

    # Check expectations
    assert runner_result.exit_code == 0


    mock_DevEnvLocalSetup.assert_called_once()

    mock_Table.assert_called_once()
    calls = [call("name"), call("address")]
    print("calls ", calls)
    mock_table.add_column.assert_has_calls(calls)

    mock_platform.config_file.deserialize["hosts"].assert_called_once()
    
    calls = []
    for host in test_hosts:
        calls.append(call(host["name"], host["address"]))
    print("calls2 ", calls)
    mock_table.add_row.assert_has_calls(calls)

    mock_stdout_print.assert_called_once_with(mock_table)

@patch("dem.cli.command.list_host_cmd.Table")
@patch("dem.cli.command.list_host_cmd.stdout.print")
@patch("dem.cli.command.list_host_cmd.DevEnvLocalSetup")
def test_list_host_non_available(mock_DevEnvLocalSetup: MagicMock, mock_stdout_print: MagicMock, 
                                mock_Table):
    print("I am running !2")
    # Test setup
    mock_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_platform
    mock_platform.config_file.deserialize["hosts"].return_value = []
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list-host"], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_DevEnvLocalSetup.assert_called_once()

    mock_Table.assert_called_once()
    calls = [call("name"), call("address")]
    mock_table.add_column.assert_has_calls(calls)

    mock_platform.config_file.deserialize["hosts"].assert_called_once_with()
    
    mock_stdout_print.assert_called_once_with("[yellow]Error: No available Hosts ![/]")