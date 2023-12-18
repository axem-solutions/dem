"""Tests for the modify command."""
# tests/cli/test_modify_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.modify_cmd as modify_cmd

# Test framework
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from rich.console import Console
import io, typer

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
    actual_tool_images = modify_cmd.get_tool_image_list(mock_tool_images)

    # Check expectations
    expected_tool_iamges = [
        ["local_and_registry_image", "local and registry"],
        ["registry_image", "registry"],
        ["local_image", "local"],
    ]
    assert actual_tool_images == expected_tool_iamges

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
    mock_platform = MagicMock()
    mock_platform.get_deserialized.return_value = mock_deserialized_local_dev_env

    # Run unit under test
    modify_cmd.handle_user_confirm("confirm", MagicMock(), mock_platform)

    # Check expectation
    mock_platform.flush_to_file.assert_called_once()

@patch("dem.cli.command.modify_cmd.typer.prompt")
def test_handle_user_confirm_save_as(mock_prompt):
    # Test setup    
    mock_prompt.return_value = "test new name"
    mock_deserialized_local_dev_env = MagicMock()
    mock_platform = MagicMock()
    mock_platform.get_deserialized.return_value = mock_deserialized_local_dev_env
    mock_platform.get_dev_env_by_name.return_value = None
    mock_dev_env_local = MagicMock()
    mock_dev_env_local.name = "fake dev env"
    mock_platform.local_dev_envs = [mock_dev_env_local]
    
    # Run unit under test
    modify_cmd.handle_user_confirm("save as", mock_dev_env_local, mock_platform)

    # Check expectation
    mock_prompt.assert_called_once_with("Name of the new Development Environment")
    mock_platform.flush_to_file.assert_called_once()

    assert "fake dev env" == mock_platform.local_dev_envs[0].name
    assert "test new name" == mock_platform.local_dev_envs[1].name

@patch("dem.cli.command.modify_cmd.typer.prompt")
def test_handle_user_confirm_save_as_already_exist(mock_prompt):
    # Test setup    
    mock_prompt.return_value = "test new name"
    mock_deserialized_local_dev_env = MagicMock()
    mock_platform = MagicMock()
    mock_platform.get_deserialized.return_value = mock_deserialized_local_dev_env
    mock_platform.get_dev_env_by_name.return_value = True
    mock_dev_env_local = MagicMock()
    mock_dev_env_local.name = "fake dev env"
    mock_platform.dev_envs = [mock_dev_env_local]
    
    # Run unit under test
    with pytest.raises(typer.Abort):
        modify_cmd.handle_user_confirm("save as", mock_dev_env_local, mock_platform)


def test_handle_user_confirm_cancel():
    # Test setup
    # Run unit under test
    with pytest.raises(typer.Abort):
        modify_cmd.handle_user_confirm("cancel", MagicMock(), MagicMock())

def test_execute_invalid_name():
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform
    mock_platform.get_dev_env_by_name.return_value = None
    test_dev_env_name =  "not existing env"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["modify", test_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)

    console = Console(file=io.StringIO())
    console.print("[red]The Development Environment doesn't exist.")
    assert console.file.getvalue() == runner_result.stderr

@patch("dem.cli.command.modify_cmd.handle_user_confirm")
@patch("dem.cli.command.modify_cmd.get_confirm_from_user")
@patch("dem.cli.command.modify_cmd.get_modifications_from_user")
@patch("dem.cli.command.modify_cmd.get_tool_image_list")
def test_execute_valid_name(mock_get_tool_image_list, mock_get_modifications_from_user, 
                            mock_get_confirm_from_user, mock_handle_user_confirm):
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform
    mock_dev_env_local = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env_local

    mock_tool_image_list = MagicMock()
    mock_get_tool_image_list.return_value = mock_tool_image_list

    mock_confirmation = MagicMock()
    mock_get_confirm_from_user.return_value = mock_confirmation
    test_dev_env_name =  "test"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["modify", test_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_get_tool_image_list.assert_called_once_with(mock_platform.tool_images)
    mock_get_modifications_from_user.assert_called_once_with(mock_dev_env_local, 
                                                             mock_tool_image_list)
    mock_get_confirm_from_user.assert_called_once()
    mock_handle_user_confirm.assert_called_once_with(mock_confirmation, mock_dev_env_local, 
                                                     mock_platform)