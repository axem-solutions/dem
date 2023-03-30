"""Tests for the create CLI command."""
# tests/cli/test_create_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

from dem.core.dev_env_setup import DevEnv

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test helpers
## Test cases

@patch("dem.cli.command.create_cmd.ToolTypeMenu")
@patch("dem.cli.command.create_cmd.ToolImageMenu")
@patch("dem.cli.command.create_cmd.get_tool_images")
@patch("dem.cli.command.create_cmd.install_to_json")
def test_execute_dev_env_creation(mock_install_to_json, mock_get_tool_images, mock_ToolImageMenu,
                                  mock_ToolTypeMenu):
    expected_dev_env_name = "test_dev_env"
    fake_tool_type_menu = MagicMock()
    mock_ToolTypeMenu.return_value = fake_tool_type_menu
    fake_tool_types = [
        "build system",
        "toolchain",
        "debugger",
        "deployer",
        "test framework"
    ]
    fake_tool_type_menu.get_selected_tool_types.return_value = fake_tool_types
    fake_tool_images = MagicMock()
    mock_get_tool_images.return_value = fake_tool_images
    fake_tool_image_menu = MagicMock()
    mock_ToolImageMenu.return_value = fake_tool_image_menu
    fake_selected_tool_images = [
        ["axemsolutions/make_gnu_arm", "latest"], 
        ["axemsolutions/make_gnu_arm", "latest"], 
        ["axemsolutions/stlink_org", "latest"], 
        ["axemsolutions/stlink_org", "latest"], 
        ["axemsolutions/cpputest", "latest"],
    ]
    fake_tool_image_menu.get_selected_tool_image.side_effect = fake_selected_tool_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["create", expected_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_ToolTypeMenu.assert_called_once_with(list(DevEnv.supported_tool_types))
    fake_tool_type_menu.wait_for_user.assert_called_once()
    fake_tool_type_menu.get_selected_tool_types.assert_called_once()
    mock_get_tool_images.assert_called_once()
    mock_ToolImageMenu.assert_called_once_with(fake_tool_images)
    calls = [
        call("Select tool image for type build system"),
        call("Select tool image for type toolchain"),
        call("Select tool image for type debugger"),
        call("Select tool image for type deployer"),
        call("Select tool image for type test framework"),
    ]
    fake_tool_image_menu.set_title.assert_has_calls(calls)
    fake_tool_image_menu.wait_for_user.assert_called()
    fake_tool_image_menu.get_selected_tool_image.assert_called()
    expected_dev_env_descriptor = {
        "name": expected_dev_env_name,
        "tools": [
            {
                "type": "build system",
                "image_name": "axemsolutions/make_gnu_arm",
                "image_version": "latest"
            },
            {
                "type": "toolchain",
                "image_name": "axemsolutions/make_gnu_arm",
                "image_version": "latest"
            },
            {
                "type": "debugger",
                "image_name": "axemsolutions/stlink_org",
                "image_version": "latest"
            },
            {
                "type": "deployer",
                "image_name": "axemsolutions/stlink_org",
                "image_version": "latest"
            },
            {
                "type": "test framework",
                "image_name": "axemsolutions/cpputest",
                "image_version": "latest"
            }
        ]
    }
    mock_install_to_json.assert_called_once_with(expected_dev_env_descriptor)