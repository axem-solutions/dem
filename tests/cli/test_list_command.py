"""Unit tests for the list CLI command."""
# tests/cli/test_list_command.py

import io
import dem.cli.main as main
from typer.testing import CliRunner
from rich.console import Console
from rich.table import Table
from unittest.mock import patch, MagicMock
import json
import tests.fake_data as fake_data

# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.cli.command.list_command.data_management.get_deserialized_dev_env_json")
@patch("dem.cli.command.list_command.container_engine.ContainerEngine")
@patch("dem.cli.command.list_command.registry.list_repos")
def test_with_valid_dev_env_json(mock_list_repos, mock_ContainerEngine,
                                 mock_get_deserialized_dev_env_json):
    test_local_images = [
        "alpine:latest",
        "make_gnu_arm:v1.0.0",
        "stlink_org:latest", 
        "stlink_org:v1.0.0",
        "cpputest:latest",
        "make_gnu_arm:latest", 
        "make_gnu_arm:v0.1.0", 
        "make_gnu_arm:v1.1.0",
        "debian:latest",
        "ubuntu:latest",
        "hello-world:latest",
    ]
    test_registry_images = [
        "make_gnu_arm:latest", 
        "cpputest:latest",
        "stlink_org:latest", 
    ]
    mock_get_deserialized_dev_env_json.return_value = json.loads(fake_data.dev_env_json)
    mock_container_engine = MagicMock()
    mock_container_engine.get_local_image_tags.return_value = test_local_images
    mock_ContainerEngine.return_value = mock_container_engine
    mock_list_repos.return_value = test_registry_images

    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--env"])

    mock_get_deserialized_dev_env_json.assert_called_once()
    mock_container_engine.get_local_image_tags.assert_called_once()
    mock_list_repos.assert_called_once()

    assert 0 == runner_result.exit_code

    expected_table = Table()
    expected_table.add_column("Development Environment")
    expected_table.add_column("Status")
    expected_table.add_row("demo", "Installed.")
    expected_table.add_row("nagy_cica_project", "[red]Error: Required image is not available![/]")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stdout

@patch("dem.cli.command.list_command.data_management.get_deserialized_dev_env_json")
def test_with_empty_dev_env_json(mock_get_deserialized_dev_env_json):
    mock_get_deserialized_dev_env_json.return_value = json.loads(fake_data.empty_dev_env_json)

    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--env"])

    mock_get_deserialized_dev_env_json.assert_called_once()

    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[yellow]No installed Development Environments.[/]")
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stdout

def test_without_options():
    runner_result = runner.invoke(main.typer_cli, ["list"], color=True)
    
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print(\
"""Usage: dem list [OPTIONS]
Try 'dem list --help' for help.

Error: You need to set the scope and what to list!""")
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stderr