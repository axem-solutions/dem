"""Tests for the delete command."""
# tests/cli/test_modify_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.delete_cmd as delete_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

from rich.console import Console
import io, docker.errors

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.cli.command.delete_cmd.typer.confirm")
@patch("dem.cli.command.delete_cmd.ContainerEngine")
def test_remove_unused_tool_images(mock_ContainerEngine, mock_confirm):
    # Test setup
    fake_dev_env1 = MagicMock()
    fake_dev_env2 = MagicMock()
    fake_deleted_dev_env = MagicMock()
    fake_dev_env1.tools = [
        {
            "type": "build_system",
            "image_name": "still_required_tool_image",
            "image_version": "latest"
        }
    ]
    fake_dev_env2.tools = fake_dev_env1.tools
    fake_deleted_dev_env.tools = [
        {
            "type": "build_system",
            "image_name": "still_required_tool_image",
            "image_version": "latest"
        },
        {
            "type": "build_system",
            "image_name": "not_required_tool_image_to_keep",
            "image_version": "latest"
        },
        {
            "type": "build_system",
            "image_name": "not_required_tool_image_to_delete",
            "image_version": "latest"
        }
    ]
    fake_dev_env_local_setup = MagicMock()
    fake_dev_env_local_setup.dev_envs = [fake_dev_env1, fake_dev_env2]
    fake_container_engine = MagicMock()
    mock_ContainerEngine.return_value = fake_container_engine
    mock_confirm.side_effect = [False, True]

    # Run unit under test
    delete_cmd.remove_unused_tool_images(fake_deleted_dev_env, fake_dev_env_local_setup)

    # Check expectations
    mock_ContainerEngine.assert_called_once()
    calls = [
        call("not_required_tool_image_to_keep:latest is not required by any Development Environment. \
              Would you like to remove it?"),
        call("not_required_tool_image_to_delete:latest is not required by any Development Environment. \
              Would you like to remove it?"),
    ]
    mock_confirm.asser_has_calls(calls)
    fake_container_engine.remove.assert_called_once_with("not_required_tool_image_to_delete:latest")

@patch("dem.cli.command.delete_cmd.stdout.print")
@patch("dem.cli.command.delete_cmd.typer.confirm")
@patch("dem.cli.command.delete_cmd.ContainerEngine")
def test_remove_unused_tool_images_ImageNotFound(mock_ContainerEngine, mock_confirm, mock_print):
    # Test setup
    fake_deleted_dev_env = MagicMock()
    fake_deleted_dev_env.tools = [
        {
            "type": "build_system",
            "image_name": "not_required_tool_image_to_delete",
            "image_version": "latest"
        }
    ]
    fake_dev_env_local_setup = MagicMock()
    fake_container_engine = MagicMock()
    mock_ContainerEngine.return_value = fake_container_engine
    mock_confirm.return_value = True
    fake_container_engine.remove.side_effect = docker.errors.ImageNotFound("dummy")

    # Run unit under test
    delete_cmd.remove_unused_tool_images(fake_deleted_dev_env, fake_dev_env_local_setup)

    # Check expectations
    mock_ContainerEngine.assert_called_once()
    mock_confirm.assert_called_once_with("not_required_tool_image_to_delete:latest is not required by any Development Environment. Would you like to remove it?")
    fake_container_engine.remove.assert_called_once_with("not_required_tool_image_to_delete:latest")
    mock_print.assert_called_once_with("[yellow]Couldn't delete not_required_tool_image_to_delete:latest, because doesn't exist.")

@patch("dem.cli.command.delete_cmd.stderr.print")
@patch("dem.cli.command.delete_cmd.typer.confirm")
@patch("dem.cli.command.delete_cmd.ContainerEngine")
def test_remove_unused_tool_images_APIError(mock_ContainerEngine, mock_confirm, mock_print):
    # Test setup
    fake_deleted_dev_env = MagicMock()
    fake_deleted_dev_env.tools = [
        {
            "type": "build_system",
            "image_name": "not_required_tool_image_to_delete",
            "image_version": "latest"
        }
    ]
    fake_dev_env_local_setup = MagicMock()
    fake_container_engine = MagicMock()
    mock_ContainerEngine.return_value = fake_container_engine
    mock_confirm.return_value = True
    fake_container_engine.remove.side_effect = docker.errors.APIError("dummy")

    # Run unit under test
    delete_cmd.remove_unused_tool_images(fake_deleted_dev_env, fake_dev_env_local_setup)

    # Check expectations
    mock_ContainerEngine.assert_called_once()
    mock_confirm.assert_called_once_with("not_required_tool_image_to_delete:latest is not required by any Development Environment. Would you like to remove it?")
    fake_container_engine.remove.assert_called_once_with("not_required_tool_image_to_delete:latest")
    mock_print.assert_called_once_with("[red]Error: not_required_tool_image_to_delete:latest is used by a container. Unable to remove it.")

@patch("dem.cli.command.delete_cmd.remove_unused_tool_images")
@patch("dem.cli.command.delete_cmd.write_deserialized_dev_env_json")
@patch("dem.cli.command.delete_cmd.DevEnvLocalSetup")
@patch("dem.cli.command.delete_cmd.read_deserialized_dev_env_json")
def test_delete_dev_env_valid_name(mock_read_deserialized_dev_env_json, mock_DevEnvLocalSetup, 
                                   mock_write_deserialized_dev_env_json, 
                                   mock_remove_unused_tool_images):
    # Test setup
    fake_dev_env1 = MagicMock()
    fake_dev_env_to_delete = MagicMock()
    fake_dev_env_to_delete.name = "dev_env"
    fake_dev_env_local_setup = MagicMock()
    fake_dev_env_local_setup.dev_envs = [fake_dev_env1, fake_dev_env_to_delete]
    fake_deserialized_dev_env_json = MagicMock()
    mock_read_deserialized_dev_env_json.return_value = fake_deserialized_dev_env_json
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env_local_setup.get_dev_env_by_name.return_value = fake_dev_env_to_delete
    fake_dev_env_local_setup.get_deserialized.return_value = fake_deserialized_dev_env_json
    
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["delete", fake_dev_env_to_delete.name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_deserialized_dev_env_json)
    fake_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(fake_dev_env_to_delete.name)
    fake_dev_env_local_setup.get_deserialized.assert_called_once()
    mock_write_deserialized_dev_env_json.assert_called_once_with(fake_deserialized_dev_env_json)
    mock_remove_unused_tool_images.assert_called_once_with(fake_dev_env_to_delete,
                                                           fake_dev_env_local_setup)

    assert fake_dev_env1 in fake_dev_env_local_setup.dev_envs
    assert fake_dev_env_to_delete not in fake_dev_env_local_setup.dev_envs

@patch("dem.cli.command.delete_cmd.DevEnvLocalSetup")
@patch("dem.cli.command.delete_cmd.read_deserialized_dev_env_json")
def test_delete_dev_env_invalid_name(mock_read_deserialized_dev_env_json, mock_DevEnvLocalSetup):
    # Test setup
    fake_dev_env_local_setup = MagicMock()
    fake_deserialized_dev_env_json = MagicMock()
    mock_read_deserialized_dev_env_json.return_value = fake_deserialized_dev_env_json
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env_local_setup.get_dev_env_by_name.return_value = None
    test_invalid_name = "test_invalid_name"
    
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["delete", test_invalid_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_deserialized_dev_env_json)
    fake_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(test_invalid_name)

    console = Console(file=io.StringIO())
    console.print("[red]The Development Environment doesn't exist.")
    assert console.file.getvalue() == runner_result.stderr