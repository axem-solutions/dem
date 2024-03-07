"""Tests for the create CLI command."""
# tests/cli/test_create_cmd.py

# Unit under test
import dem.cli.main as main
import dem.cli.command.create_cmd as create_cmd

# Test framework
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

from dem.core.tool_images import ToolImages

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

def test_get_tool_image_list():
    # Test setup
    mock_tool_images = MagicMock()
    mock_tool_images.registry.elements = [
        "local_and_registry_image",
        "registry_image",
    ]
    mock_tool_images.local.elements = [
        "local_image",
        "local_and_registry_image",
    ]

    # Run unit under test
    actual_tool_images = create_cmd.get_tool_image_list(mock_tool_images)

    # Check expectations
    expected_tool_iamges = [
        ["local_and_registry_image", "local and registry"],
        ["registry_image", "registry"],
        ["local_image", "local"],
    ]
    assert actual_tool_images == expected_tool_iamges

def test_overwrite_existing_dev_env():
    # Test setup
    mock_original_dev_env = MagicMock()
    mock_original_dev_env.tools = MagicMock()

    mock_tools = MagicMock()
    mock_new_dev_env_descriptor = {
        "tools": mock_tools
    }

    # Run unit under test
    create_cmd.overwrite_existing_dev_env(mock_original_dev_env, mock_new_dev_env_descriptor)

    # Check expectations
    assert mock_original_dev_env.tools == mock_tools

@patch("dem.cli.command.create_cmd.DevEnv")
def test_create_new_dev_env(mock_DevEnvLocal):
    # Test setup
    mock_new_dev_env = MagicMock()
    mock_DevEnvLocal.return_value = mock_new_dev_env

    mock_platform = MagicMock()
    mock_new_dev_env_descriptor = MagicMock()

    # Run unit under test
    create_cmd.create_new_dev_env(mock_platform, mock_new_dev_env_descriptor)

    # Check expectations
    mock_DevEnvLocal.assert_called_once_with(mock_new_dev_env_descriptor)
    mock_platform.local_dev_envs.append.assert_called_once_with(mock_new_dev_env)

@patch("dem.cli.command.create_cmd.create_new_dev_env")
@patch("dem.cli.command.create_cmd.get_dev_env_descriptor_from_user")
@patch("dem.cli.command.create_cmd.get_tool_image_list")
def test_create_dev_env_new(mock_get_tool_image_list, mock_get_dev_env_descriptor_from_user, 
                            mock_create_new_dev_env):
    # Test setup
    mock_dev_env_local_setup = MagicMock()
    mock_dev_env_local_setup.get_dev_env_by_name.return_value = None

    mock_tool_images = MagicMock()
    mock_get_tool_image_list.return_value = mock_tool_images

    mock_dev_env_descriptor = MagicMock()
    mock_get_dev_env_descriptor_from_user.return_value = mock_dev_env_descriptor

    mock_new_dev_env = MagicMock()
    mock_create_new_dev_env.return_value = mock_new_dev_env

    expected_dev_env_name = "test_dev_env"

    # Run unit under test
    create_cmd.create_dev_env(mock_dev_env_local_setup, expected_dev_env_name)

    # Check expectations
    mock_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(expected_dev_env_name)
    mock_get_tool_image_list.assert_called_once_with(mock_dev_env_local_setup.tool_images)
    mock_get_dev_env_descriptor_from_user.assert_called_once_with(expected_dev_env_name, mock_tool_images)
    mock_create_new_dev_env.assert_called_once_with(mock_dev_env_local_setup, mock_dev_env_descriptor)
    mock_new_dev_env.check_image_availability.return_value = mock_dev_env_local_setup.tool_images

@patch("dem.cli.command.create_cmd.overwrite_existing_dev_env")
@patch("dem.cli.command.create_cmd.get_dev_env_descriptor_from_user")
@patch("dem.cli.command.create_cmd.get_tool_image_list")
@patch("dem.cli.command.create_cmd.typer.confirm")
def test_create_dev_env_overwrite(mock_confirm, mock_get_tool_image_list, 
                                  mock_get_dev_env_descriptor_from_user,
                                  mock_overwrite_existing_dev_env):
    # Test setup
    mock_dev_env_local_setup = MagicMock()
    mock_dev_env_original = MagicMock()
    mock_dev_env_local_setup.get_dev_env_by_name.return_value = mock_dev_env_original
    mock_tools = MagicMock()
    mock_dev_env_descriptor = {
        "tools": mock_tools
    }

    mock_tool_images = MagicMock()
    mock_get_tool_image_list.return_value = mock_tool_images

    mock_get_dev_env_descriptor_from_user.return_value = mock_dev_env_descriptor

    expected_dev_env_name = "test_dev_env"

    # Run unit under test
    create_cmd.create_dev_env(mock_dev_env_local_setup, expected_dev_env_name)

    # Check expectations
    mock_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(expected_dev_env_name)
    mock_confirm.assert_called_once_with("The input name is already used by a Development Environment. Overwrite it?",
                                         abort=True)
    mock_get_tool_image_list(mock_dev_env_local_setup.tool_images)
    mock_get_dev_env_descriptor_from_user.assert_called_once_with(expected_dev_env_name,
                                                                  mock_tool_images)
    mock_overwrite_existing_dev_env.assert_called_once_with(mock_dev_env_original, mock_dev_env_descriptor)

@patch("dem.cli.command.create_cmd.get_dev_env_descriptor_from_user")
@patch("dem.cli.command.create_cmd.typer.confirm")
def test_execute_abort(mock_confirm, mock_get_dev_env_descriptor_from_user):
    # Test setup
    mock_dev_env_local_setup = MagicMock()
    mock_dev_env_original = MagicMock()
    mock_dev_env_local_setup.get_dev_env_by_name.return_value = mock_dev_env_original
    mock_confirm.side_effect = Exception()
    expected_dev_env_name = "test_dev_env"

    # Run unit under test
    # The exception doesn't metter, only the fact that the function execution has stopped.
    with pytest.raises(Exception):
        create_cmd.create_dev_env(mock_dev_env_local_setup, expected_dev_env_name)

        # Check expectations
        mock_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(expected_dev_env_name)
        mock_confirm.assert_called_once_with("The input name is already used by a Development Environment. Overwrite it?",
                                            abort=True)
        mock_get_dev_env_descriptor_from_user.assert_not_called()

@patch("dem.cli.command.create_cmd.stdout.print")
@patch("dem.cli.command.create_cmd.create_dev_env")
def test_execute(mock_create_dev_env, mock_stdout_print):
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_dev_env = MagicMock()
    expected_dev_env_name = "test_dev_env"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["create", expected_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_create_dev_env.assert_called_once_with(mock_platform, expected_dev_env_name)
    mock_platform.flush_descriptors.assert_called_once()
    mock_stdout_print.assert_has_calls([
        call(f"The [green]{expected_dev_env_name}[/] Development Environment has been created!"),
        call("Run [italic]dem install[/] to install it.")
    ])

@patch("dem.cli.command.create_cmd.stderr.print")
@patch("dem.cli.command.create_cmd.create_dev_env")
def test_execute_failure(mock_create_dev_env, mock_stderr_print):
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    expected_dev_env_name = "test_dev_env"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["create", expected_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_create_dev_env.assert_called_once_with(mock_platform, expected_dev_env_name)

@patch("dem.cli.command.create_cmd.stderr.print")
def test_create_dev_env_with_whitespace(mock_stderr_print):
    # Test setup
    mock_dev_env_local_setup = MagicMock()
    mock_dev_env_local_setup.get_dev_env_by_name.return_value = None

    mock_tool_images = MagicMock()
    mock_dev_env_local_setup.tool_images = mock_tool_images

    expected_dev_env_name = "test dev env with space"

    # Run unit under test
    with pytest.raises(Exception):
        create_cmd.create_dev_env(mock_dev_env_local_setup, expected_dev_env_name)

    # Check expectations
    mock_dev_env_local_setup.get_dev_env_by_name.assert_not_called()
    mock_stderr_print.assert_called_once_with("The name of the Development Environment cannot contain whitespace characters!")