"""Unit tests for the info CLI command."""
# tests/cli/test_info_command.py

from typer.testing import CliRunner
import dem.cli.main as main
from unittest.mock import patch
import docker 
from rich.console import Console
from rich.table import Table
import io
import tests.fake_data as fake_data
import json

runner = CliRunner(mix_stderr=False)

class mockImage:
    def __init__(self, tags: list[str]):
        self.tags = tags

def get_test_image_list() -> list[mockImage]:
    test_image_list = []
    test_image_list.append(mockImage(["alpine:latest"]))
    test_image_list.append(mockImage([""]))
    test_image_list.append(mockImage(["make_gnu_arm:v1.0.0"]))
    test_image_list.append(mockImage(["stlink_org:latest", "stlink_org:v1.0.0'"]))
    test_image_list.append(mockImage(["cpputest:latest"]))
    test_image_list.append(mockImage(["make_gnu_arm:latest"]))
    test_image_list.append(mockImage(["debian:latest"]))
    test_image_list.append(mockImage(["ubuntu:latest"]))
    test_image_list.append(mockImage(["hello-world:latest"]))
    test_image_list.append(mockImage([""]))
    return test_image_list

test_docker_client = docker.from_env()

@patch("dem.cli.dev_env.info_command.data_management.get_deserialized_dev_env_json")
@patch("dem.cli.dev_env.info_command.image_management.get_local_image_tags")
def test_info_arg_demo(mock_get_local_image_tags, 
                        mock_get_deserialized_dev_env_json):
    test_image_tags = [
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
    #Mocks
    mock_get_deserialized_dev_env_json.return_value = json.loads(fake_data.dev_env_json)
    mock_get_local_image_tags.return_value = test_image_tags

    runner_result = runner.invoke(main.typer_cli, ["dev_env", "info", "demo"], color=True)

    mock_get_deserialized_dev_env_json.assert_called_once()

    expected_table = Table()
    expected_table.add_column("Type")
    expected_table.add_column("Image")
    expected_table.add_row("build system", "make_gnu_arm:latest")
    expected_table.add_row("toolchain", "make_gnu_arm:latest")
    expected_table.add_row("debugger", "stlink_org:latest")
    expected_table.add_row("deployer", "stlink_org:latest")
    expected_table.add_row("test framework", "cpputest:latest")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    expected_output = console.file.getvalue()

    assert 0 == runner_result.exit_code

    assert expected_output == runner_result.stdout


@patch("dem.cli.dev_env.info_command.data_management.get_deserialized_dev_env_json")
@patch("dem.cli.dev_env.info_command.image_management.get_local_image_tags")
def test_info_arg_nagy_cica_project(mock_get_local_image_tags, 
                                    mock_get_deserialized_dev_env_json):
    test_image_tags = [
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
    #Mocks
    mock_get_deserialized_dev_env_json.return_value = json.loads(fake_data.dev_env_json)
    mock_get_local_image_tags.return_value = test_image_tags

    runner_result = runner.invoke(main.typer_cli, ["dev_env", "info", "nagy_cica_project"], color=True)

    mock_get_deserialized_dev_env_json.assert_called_once()

    expected_table = Table()
    expected_table.add_column("Type")
    expected_table.add_column("Image")
    expected_table.add_row("build system", "[red]Error: missing image![/]")
    expected_table.add_row("toolchain", "[red]Error: missing image![/]")
    expected_table.add_row("debugger", "[red]Error: missing image![/]")
    expected_table.add_row("deployer", "[red]Error: missing image![/]")
    expected_table.add_row("test framework", "cpputest:latest")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    expected_output = console.file.getvalue()

    assert 0 == runner_result.exit_code

    assert expected_output == runner_result.stdout

def test_info_arg_invalid():
    runner_result = runner.invoke(main.typer_cli, ["dev_env", "info", "not_existing_environment"])

    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[red]Error: Unknown Development Environment: not_existing_environment[/]")
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stderr