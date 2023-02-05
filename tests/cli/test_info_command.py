# tests/cli/test_info_command.py

from typer.testing import CliRunner
import dem.cli.main as main
from unittest.mock import patch, MagicMock
import docker 
from rich.console import Console
from rich.table import Table

runner = CliRunner()

test_image_list = """[<Image: 'alpine:latest'>, <Image: ''>, <Image: 'make_gnu_arm:v1.0.0'>, <Image: 'stlink_org:latest', 'stlink_org:v1.0.0'>, <Image: 'cpputest:latest'>, <Image: 'make_gnu_arm:latest'>, <Image: 'debian:latest'>, <Image: 'ubuntu:latest'>, <Image: 'hello-world:latest'>]"""
test_docker_client = docker.from_env()

@patch("dem.cli.info_command.data_management.get_deserialized_dev_env_json")
@patch("docker.from_env")
def test_info(mock_docker_from_env, mock_get_deserialized_dev_env_json):
    #Mocks
    test_docker_client = MagicMock()
    mock_docker_from_env.return_value = test_docker_client

    result = runner.invoke(main.dem_typer_cli, "info")

    mock_get_deserialized_dev_env_json.assert_called_once()
    test_docker_client.images.list.assert_called_once()

    # expected_table = Table()
    # expected_table.add_column("")
    assert 0 == result.exit_code