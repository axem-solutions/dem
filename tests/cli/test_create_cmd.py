"""Tests for the create CLI command."""
# tests/cli/test_create_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.create_cmd as create_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

from dem.core.dev_env_setup import DevEnv
from dem.core.tool_images import ToolImages

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test helpers
## Test cases

@patch("dem.cli.command.create_cmd.ToolImages")
def test_get_tool_images(mock_ToolImages):
    # Test setup
    fake_elements = {
        "local_image": ToolImages.LOCAL_ONLY,
        "local_and_registry_image": ToolImages.LOCAL_AND_REGISTRY,
        "registry_image": ToolImages.REGISTRY_ONLY
    }
    fake_tool_images = MagicMock()
    fake_tool_images.elements = fake_elements
    mock_ToolImages.return_value = fake_tool_images

    # Run unit under test
    actual_tool_images = create_cmd.get_tool_images()

    # Check expectations
    mock_ToolImages.assert_called_once()

    expected_tool_iamges = [
        ["local_image", "local"],
        ["local_and_registry_image", "local and registry"],
        ["registry_image", "registry"]
    ]
    assert actual_tool_images == expected_tool_iamges

@patch("dem.cli.command.create_cmd.ToolTypeMenu")
@patch("dem.cli.command.create_cmd.ToolImageMenu")
@patch("dem.cli.command.create_cmd.get_tool_images")
def test_get_dev_env_descriptor_from_user(mock_get_tool_images, mock_ToolImageMenu,
                                          mock_ToolTypeMenu):
    # Test setup
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
    actual_dev_env_descriptor = create_cmd.get_dev_env_descriptor_from_user(expected_dev_env_name)

    # Check expectations
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
    assert expected_dev_env_descriptor == actual_dev_env_descriptor

@patch("dem.cli.command.create_cmd.data_management.write_deserialized_dev_env_json")
@patch("dem.cli.command.create_cmd.DevEnvLocal")
@patch("dem.cli.command.create_cmd.get_dev_env_descriptor_from_user")
@patch("dem.cli.command.create_cmd.DevEnvLocalSetup")
@patch("dem.cli.command.create_cmd.data_management.read_deserialized_dev_env_json")
def test_execute_dev_env_creation(mock_read_deserialized_dev_env_json, mock_DevEnvLocalSetup,
                                  mock_get_dev_env_descriptor_from_user,
                                  mock_DevEnvLocal, mock_write_deserialized_dev_env_json):
    # Test setup
    fake_deserialized_local_dev_env = MagicMock()
    mock_read_deserialized_dev_env_json.return_value = fake_deserialized_local_dev_env
    fake_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env_local_setup.get_dev_env_by_name.return_value = None
    fake_dev_env_descriptor = MagicMock()
    mock_get_dev_env_descriptor_from_user.return_value = fake_dev_env_descriptor
    fake_dev_env_local_setup.get_deserialized.return_value = fake_deserialized_local_dev_env
    expected_dev_env_name = "test_dev_env"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["create", expected_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_deserialized_local_dev_env)
    fake_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(expected_dev_env_name)
    mock_get_dev_env_descriptor_from_user.assert_called_once_with(expected_dev_env_name)
    mock_DevEnvLocal.assert_called_once_with(fake_dev_env_descriptor)
    fake_dev_env_local_setup.get_deserialized.assert_called_once()
    mock_write_deserialized_dev_env_json.assert_called_once_with(fake_deserialized_local_dev_env)

@patch("dem.cli.command.create_cmd.data_management.write_deserialized_dev_env_json")
@patch("dem.cli.command.create_cmd.get_dev_env_descriptor_from_user")
@patch("dem.cli.command.create_cmd.typer.confirm")
@patch("dem.cli.command.create_cmd.DevEnvLocalSetup")
@patch("dem.cli.command.create_cmd.data_management.read_deserialized_dev_env_json")
def test_execute_dev_env_overwrite(mock_read_deserialized_dev_env_json, mock_DevEnvLocalSetup,
                                   mock_confirm,
                                   mock_get_dev_env_descriptor_from_user,
                                   mock_write_deserialized_dev_env_json):
    # Test setup
    fake_deserialized_local_dev_env = MagicMock()
    mock_read_deserialized_dev_env_json.return_value = fake_deserialized_local_dev_env
    fake_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env_original = MagicMock()
    fake_dev_env_local_setup.get_dev_env_by_name.return_value = fake_dev_env_original
    fake_tools = MagicMock()
    fake_dev_env_descriptor = {
        "tools": fake_tools
    }
    mock_get_dev_env_descriptor_from_user.return_value = fake_dev_env_descriptor
    fake_dev_env_local_setup.get_deserialized.return_value = fake_deserialized_local_dev_env
    expected_dev_env_name = "test_dev_env"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["create", expected_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_deserialized_local_dev_env)
    fake_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(expected_dev_env_name)
    mock_confirm.assert_called_once_with("The input name is already used by a Development Environment. Overwrite it?",
                                         abort=True)
    mock_get_dev_env_descriptor_from_user.assert_called_once_with(expected_dev_env_name)
    assert fake_dev_env_original.tools == fake_tools
    fake_dev_env_local_setup.get_deserialized.assert_called_once()
    mock_write_deserialized_dev_env_json.assert_called_once_with(fake_deserialized_local_dev_env)

@patch("dem.cli.command.create_cmd.get_dev_env_descriptor_from_user")
@patch("dem.cli.command.create_cmd.typer.confirm")
@patch("dem.cli.command.create_cmd.DevEnvLocalSetup")
@patch("dem.cli.command.create_cmd.data_management.read_deserialized_dev_env_json")
def test_execute_abort(mock_read_deserialized_dev_env_json, mock_DevEnvLocalSetup, 
                       mock_confirm, mock_get_dev_env_descriptor_from_user):
    # Test setup
    fake_deserialized_local_dev_env = MagicMock()
    mock_read_deserialized_dev_env_json.return_value = fake_deserialized_local_dev_env
    fake_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env_original = MagicMock()
    fake_dev_env_local_setup.get_dev_env_by_name.return_value = fake_dev_env_original
    mock_confirm.side_effect = Exception()
    expected_dev_env_name = "test_dev_env"

    # Run unit under test
    runner.invoke(main.typer_cli, ["create", expected_dev_env_name], color=True)

    # Check expectations
    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_deserialized_local_dev_env)
    fake_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(expected_dev_env_name)
    mock_confirm.assert_called_once_with("The input name is already used by a Development Environment. Overwrite it?",
                                         abort=True)
    mock_get_dev_env_descriptor_from_user.assert_not_called()
