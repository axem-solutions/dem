"""Tests for the modify command."""
# tests/cli/test_modify_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.modify_cmd as modify_cmd

# Test framework
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

from dem.core.dev_env_setup import DevEnv
from dem.core.tool_images import ToolImages
from rich.console import Console
import io, typer

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

def test_get_tool_image_list():
    # Test setup
    mock_tool_images = MagicMock()
    mock_tool_images.elements = {
        "local_image:latest": ToolImages.LOCAL_ONLY,
        "registry_image:latest": ToolImages.REGISTRY_ONLY,
        "local_and_registry_image:latest": ToolImages.LOCAL_AND_REGISTRY
    }

    # Run unit under test
    actual_tool_images = modify_cmd.get_tool_image_list(mock_tool_images)

    # Check expectations
    expected_tool_images = [
        ["local_image:latest", "local"],
        ["registry_image:latest", "registry"],
        ["local_and_registry_image:latest", "local and registry"]
    ]
    assert expected_tool_images == actual_tool_images

@patch("dem.cli.command.modify_cmd.ToolTypeMenu")
@patch("dem.cli.command.modify_cmd.ToolImageMenu")
def test_get_modifications_from_user(mock_ToolImageMenu, mock_ToolTypeMenu):
    # Test setup
    mock_tool_type_menu = MagicMock()
    mock_ToolTypeMenu.return_value = mock_tool_type_menu
    mock_selected_tool_types = [
        "already_present_tool_type",
        "new_tool_type1",
        "new_tool_type2"
    ]
    mock_tool_type_menu.get_selected_tool_types.return_value = mock_selected_tool_types
    mock_available_tool_images = [
        ["tool_image1:latest", "local and registry"],
        ["tool_image2:latest", "local and registry"],
        ["tool_image3:latest", "local and registry"]
    ]
    mock_tool_image_menu = MagicMock()
    mock_ToolImageMenu.return_value = mock_tool_image_menu
    mock_selected_tool_images = [
        ["tool_image1", "latest"],
        ["tool_image2", "latest"],
        ["tool_image3", "latest"]
    ]
    mock_tool_image_menu.get_selected_tool_image.side_effect = mock_selected_tool_images

    test_dev_env = MagicMock()
    test_dev_env.tools = [
        {
            "type": "already_present_tool_type",
            "image_name": "tool_image2",
            "image_version": "latest"
        },
        {
            "type": "tool_type_to_remove",
            "image_name": "prev_tool_image",
            "image_version": "latest"
        }
    ]

    mock_tool_image_list = MagicMock()

    # Run unit under test
    modify_cmd.get_modifications_from_user(test_dev_env, mock_tool_image_list)

    # Check expectations
    mock_ToolTypeMenu.assert_called_once_with(list(DevEnv.supported_tool_types))
    mock_tool_type_menu.preset_selection.assert_called_once_with(["already_present_tool_type", 
                                                                  "tool_type_to_remove"])
    mock_tool_type_menu.wait_for_user.assert_called_once()
    mock_tool_type_menu.get_selected_tool_types.assert_called_once()
    mock_ToolImageMenu.assert_called_once_with(mock_tool_image_list)

    mock_tool_image_menu.set_cursor.assert_called_once_with("tool_image2:latest")

    calls = [
        call("Select tool image for type already_present_tool_type -- not modified"),
        call("Select tool image for type new_tool_type1 -- [yellow]new![/]"),
        call("Select tool image for type new_tool_type2 -- [yellow]new![/]"),
    ]
    mock_tool_image_menu.set_title.assert_has_calls(calls)
    mock_tool_image_menu.wait_for_user.assert_called()
    mock_tool_image_menu.get_selected_tool_image.assert_called()

    expected_tools = [
        {
            "type": "already_present_tool_type",
            "image_name": "tool_image1",
            "image_version": "latest"
        },
        {
            "type": "new_tool_type1",
            "image_name": "tool_image2",
            "image_version": "latest"
        },
        {
            "type": "new_tool_type2",
            "image_name": "tool_image3",
            "image_version": "latest"
        }
    ]
    assert expected_tools == test_dev_env.tools

@patch("dem.cli.command.modify_cmd.SelectMenu")
def test_get_confirm_from_user(mock_SelectMenu):
    # Test setup
    mock_select_menu = MagicMock()
    mock_SelectMenu.return_value = mock_select_menu
    expected_selected_item = "confirm"
    mock_select_menu.get_selected.return_value = expected_selected_item

    # Run unit under test
    actual_selected_item = modify_cmd.get_confirm_from_user()

    # Check expectations
    expected_menu_items = ["confirm", "save as", "cancel"]
    mock_SelectMenu.assert_called_once_with(expected_menu_items)
    mock_select_menu.set_title.assert_called_once_with("Are you sure to overwrite the Development Environment?")
    mock_select_menu.wait_for_user.assert_called_once()

    assert actual_selected_item == expected_selected_item

def test_handle_user_confirm_confirmed():
    # Test setup
    mock_deserialized_local_dev_env = MagicMock()
    mock_dev_env_local_setup = MagicMock()
    mock_dev_env_local_setup.get_deserialized.return_value = mock_deserialized_local_dev_env

    # Run unit under test
    modify_cmd.handle_user_confirm("confirm", MagicMock(), mock_dev_env_local_setup)

    # Check expectation
    mock_dev_env_local_setup.update_json.assert_called_once()

@patch("dem.cli.command.modify_cmd.typer.prompt")
def test_handle_user_confirm_save_as(mock_prompt):
    # Test setup
    mock_prompt.return_value = "test new name"
    mock_deserialized_local_dev_env = MagicMock()
    mock_dev_env_local_setup = MagicMock()
    mock_dev_env_local_setup.get_deserialized.return_value = mock_deserialized_local_dev_env
    mock_dev_env_local = MagicMock()
    mock_dev_env_local.name = "fake dev env"
    mock_dev_env_local_setup.dev_envs = [mock_dev_env_local]

    # Run unit under test
    modify_cmd.handle_user_confirm("save as", mock_dev_env_local, mock_dev_env_local_setup)

    # Check expectation
    mock_prompt.assert_called_once_with("Name of the new Development Environment")
    mock_dev_env_local_setup.update_json.assert_called_once()

    assert "fake dev env" == mock_dev_env_local_setup.dev_envs[0].name
    assert "test new name" == mock_dev_env_local_setup.dev_envs[1].name

def test_handle_user_confirm_cancel():
    # Test setup
    # Run unit under test
    with pytest.raises(typer.Abort):
        modify_cmd.handle_user_confirm("cancel", MagicMock(), MagicMock())

@patch("dem.cli.command.modify_cmd.DevEnvLocalSetup")
def test_execute_invalid_name(mock_DevEnvLocalSetup):
    # Test setup
    mock_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_dev_env_local_setup
    mock_dev_env_local_setup.get_dev_env_by_name.return_value = None
    test_dev_env_name =  "not existing env"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["modify", test_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_DevEnvLocalSetup.assert_called_once()
    mock_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)

    console = Console(file=io.StringIO())
    console.print("[red]The Development Environment doesn't exist.")
    assert console.file.getvalue() == runner_result.stderr

@patch("dem.cli.command.modify_cmd.handle_user_confirm")
@patch("dem.cli.command.modify_cmd.get_confirm_from_user")
@patch("dem.cli.command.modify_cmd.get_modifications_from_user")
@patch("dem.cli.command.modify_cmd.get_tool_image_list")
@patch("dem.cli.command.modify_cmd.DevEnvLocalSetup")
def test_execute_valid_name(mock_DevEnvLocalSetup, mock_get_tool_image_list, 
                            mock_get_modifications_from_user, 
                            mock_get_confirm_from_user, mock_handle_user_confirm):
    # Test setup
    mock_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_dev_env_local_setup
    mock_dev_env_local = MagicMock()
    mock_dev_env_local_setup.get_dev_env_by_name.return_value = mock_dev_env_local

    mock_tool_image_list = MagicMock()
    mock_get_tool_image_list.return_value = mock_tool_image_list

    mock_confirmation = MagicMock()
    mock_get_confirm_from_user.return_value = mock_confirmation
    test_dev_env_name =  "test"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["modify", test_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_DevEnvLocalSetup.assert_called_once()
    mock_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_get_tool_image_list.assert_called_once_with(mock_dev_env_local_setup.tool_images)
    mock_get_modifications_from_user.assert_called_once_with(mock_dev_env_local, 
                                                             mock_tool_image_list)
    mock_get_confirm_from_user.assert_called_once()
    mock_handle_user_confirm.assert_called_once_with(mock_confirmation, mock_dev_env_local, 
                                                     mock_dev_env_local_setup)