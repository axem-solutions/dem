"""Tests for the delete command."""
# tests/cli/test_modify_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.delete_cmd as delete_cmd

# Test framework
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

from dem.core.tool_images import ToolImages

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
        call("not_required_tool_image_to_keep is not required by any Development Environment. \
              Would you like to remove it?"),
        call("not_required_tool_image_to_delete is not required by any Development Environment. \
              Would you like to remove it?"),
    ]
    mock_confirm.asser_has_calls(calls)
    fake_container_engine.remove.assert_called_once_with("not_required_tool_image_to_delete:latest")

@patch("dem.cli.command.delete_cmd.remove_unused_tool_images")
@patch("dem.cli.command.delete_cmd.write_deserialized_dev_env_json")
@patch("dem.cli.command.delete_cmd.DevEnvLocalSetup")
@patch("dem.cli.command.delete_cmd.read_deserialized_dev_env_json")
def test_delete_dev_env(mock_read_deserialized_dev_env_json, mock_DevEnvLocalSetup, 
                        mock_write_deserialized_dev_env_json, mock_remove_unused_tool_images):
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