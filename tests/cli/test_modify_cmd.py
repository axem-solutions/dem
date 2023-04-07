"""Tests for the modify command."""
# tests/cli/test_modify_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.modify_cmd as modify_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

from dem.core.dev_env_setup import DevEnvLocalSetup, DevEnvLocal, DevEnv
from dem.core.tool_images import ToolImages
from rich.console import Console
import io

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.cli.command.modify_cmd.ToolImages")
def test_get_tool_images(mock_ToolImages):
    # Test setup
    fake_tool_images = MagicMock()
    fake_tool_images.elements = {
        "local_image:latest": ToolImages.LOCAL_ONLY,
        "registry_image:latest": ToolImages.REGISTRY_ONLY,
        "local_and_registry_image:latest": ToolImages.LOCAL_AND_REGISTRY
    }
    mock_ToolImages.return_value = fake_tool_images

    # Run unit under test
    actual_tool_images = modify_cmd.get_tool_images()

    # Check expectations
    expected_tool_images = [
        ["local_image:latest", "local"],
        ["registry_image:latest", "registry"],
        ["local_and_registry_image:latest", "local and registry"]
    ]
    assert expected_tool_images == actual_tool_images

@patch("dem.cli.command.modify_cmd.get_tool_images")
@patch("dem.cli.command.modify_cmd.ToolTypeMenu")
@patch("dem.cli.command.modify_cmd.ToolImageMenu")
def test_get_modifications_from_user(mock_ToolImageMenu, mock_ToolTypeMenu, mock_get_tool_images):
    # Test setup
    fake_tool_type_menu = MagicMock()
    mock_ToolTypeMenu.return_value = fake_tool_type_menu
    fake_selected_tool_types = [
        "already_present_tool_type",
        "new_tool_type1",
        "new_tool_type2"
    ]
    fake_tool_type_menu.get_selected_tool_types.return_value = fake_selected_tool_types
    fake_available_tool_images = [
        ["tool_image1:latest", "local and registry"],
        ["tool_image2:latest", "local and registry"],
        ["tool_image3:latest", "local and registry"]
    ]
    mock_get_tool_images.return_value = fake_available_tool_images
    fake_tool_image_menu = MagicMock()
    mock_ToolImageMenu.return_value = fake_tool_image_menu
    fake_selected_tool_images = [
        ["tool_image1", "latest"],
        ["tool_image2", "latest"],
        ["tool_image3", "latest"]
    ]
    fake_tool_image_menu.get_selected_tool_image.side_effect = fake_selected_tool_images

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

    # Run unit under test
    modify_cmd.get_modifications_from_user(test_dev_env)

    # Check expectations
    mock_ToolTypeMenu.assert_called_once_with(list(DevEnv.supported_tool_types))
    fake_tool_type_menu.preset_selection.assert_called_once_with(["already_present_tool_type", 
                                                                  "tool_type_to_remove"])
    fake_tool_type_menu.wait_for_user.assert_called_once()
    fake_tool_type_menu.get_selected_tool_types.assert_called_once()
    mock_ToolImageMenu.assert_called_once_with(fake_available_tool_images)

    fake_tool_image_menu.set_cursor.assert_called_once_with("tool_image2:latest")

    calls = [
        call("Select tool image for type already_present_tool_type -- not modified"),
        call("Select tool image for type new_tool_type1 -- [yellow]new![/]"),
        call("Select tool image for type new_tool_type2 -- [yellow]new![/]"),
    ]
    fake_tool_image_menu.set_title.assert_has_calls(calls)
    fake_tool_image_menu.wait_for_user.assert_called()
    fake_tool_image_menu.get_selected_tool_image.assert_called()

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
    fake_select_menu = MagicMock()
    mock_SelectMenu.return_value = fake_select_menu

    # Run unit under test
    modify_cmd.get_confirm_from_user()

    # Check expectations
    expected_menu_items = ["confirm", "save as", "cancel"]
    mock_SelectMenu.assert_called_once_with(expected_menu_items)
    fake_select_menu.set_title.assert_called_once_with("Are you sure to overwrite the Development Environment?")
    fake_select_menu.wait_for_user.assert_called_once()

@patch("dem.cli.command.modify_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.modify_cmd.DevEnvLocalSetup")
def test_execute_invalid_name(mock_DevEnvLocalSetup, mock_read_deserialized_dev_env_json):
    # Test setup
    fake_deserialized_local_dev_env = MagicMock()
    mock_read_deserialized_dev_env_json.return_value = fake_deserialized_local_dev_env
    fake_dev_env_local_setup = MagicMock(DevEnvLocalSetup)
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env_local_setup.get_dev_env_by_name.return_value = None
    test_dev_env_name =  "not existing env"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["modify", test_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once()
    fake_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)

    console = Console(file=io.StringIO())
    console.print("[red]The Development Environment doesn't exist.")
    assert console.file.getvalue() == runner_result.stderr

@patch("dem.cli.command.modify_cmd.get_confirm_from_user")
@patch("dem.cli.command.modify_cmd.get_modifications_from_user")
@patch("dem.cli.command.modify_cmd.data_management.write_deserialized_dev_env_json")
@patch("dem.cli.command.modify_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.modify_cmd.DevEnvLocalSetup")
def test_execute_valid_name(mock_DevEnvLocalSetup, mock_read_deserialized_dev_env_json,
                            mock_write_deserialized_dev_env_json, mock_get_modifications_from_user,
                            mock_get_confirm_from_user):
    # Test setup
    fake_deserialized_local_dev_env = MagicMock()
    mock_read_deserialized_dev_env_json.return_value = fake_deserialized_local_dev_env
    fake_dev_env_local_setup = MagicMock(DevEnvLocalSetup)
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env = MagicMock(DevEnvLocal)
    fake_dev_env_local_setup.get_dev_env_by_name.return_value = fake_dev_env
    fake_dev_env_local_setup.get_deserialized.return_value = fake_deserialized_local_dev_env
    test_dev_env_name =  "test"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["modify", test_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once()
    fake_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_get_modifications_from_user.assert_called_once_with(fake_dev_env)
    mock_get_confirm_from_user.assert_called_once()
    fake_dev_env_local_setup.get_deserialized.assert_called_once()
    mock_write_deserialized_dev_env_json.assert_called_once_with(fake_deserialized_local_dev_env)