# tests/cli/test_info_command.py

from typer.testing import CliRunner
import dem.cli.main as main
from unittest.mock import patch, MagicMock
import docker 
from rich.console import Console
from rich.table import Table
import io
import tests.cli.test_data as test_data
import json

runner = CliRunner()

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

@patch("dem.cli.info_command.data_management.get_deserialized_dev_env_json")
@patch("docker.from_env")
def test_info_arg_demo(mock_docker_from_env, mock_get_deserialized_dev_env_json):
    #Mocks
    mock_get_deserialized_dev_env_json.return_value = json.loads(test_data.dev_env_json)
    test_docker_client = MagicMock()
    mock_docker_from_env.return_value = test_docker_client
    test_docker_client.images.list.return_value = get_test_image_list()

    runner_result = runner.invoke(main.dem_typer_cli, ["info", "demo"], color=True)

    mock_get_deserialized_dev_env_json.assert_called_once()
    test_docker_client.images.list.assert_called_once()

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


@patch("dem.cli.info_command.data_management.get_deserialized_dev_env_json")
@patch("docker.from_env")
def test_info_arg_nagy_cica_project(mock_docker_from_env, mock_get_deserialized_dev_env_json):
    #Mocks
    mock_get_deserialized_dev_env_json.return_value = json.loads(test_data.dev_env_json)
    test_docker_client = MagicMock()
    mock_docker_from_env.return_value = test_docker_client
    test_docker_client.images.list.return_value = get_test_image_list()

    runner_result = runner.invoke(main.dem_typer_cli, ["info", "nagy_cica_project"], color=True)

    mock_get_deserialized_dev_env_json.assert_called_once()
    test_docker_client.images.list.assert_called_once()

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