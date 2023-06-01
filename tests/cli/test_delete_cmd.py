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
runner = CliRunner()

@patch("dem.cli.command.delete_cmd.stdout.print")
@patch("dem.cli.command.delete_cmd.typer.confirm")
def test_try_to_delete_tool_image_ImageNotFound(mock_confirm, mock_print):
    # Test setup
    test_tool_image = "not_required_tool_image_to_delete:latest"
    mock_dev_env_local_setup = MagicMock()
    mock_confirm.return_value = True
    mock_dev_env_local_setup.container_engine.remove.side_effect = docker.errors.ImageNotFound("dummy")

    # Run unit under test
    delete_cmd.try_to_delete_tool_image(test_tool_image, mock_dev_env_local_setup)

    # Check expectations
    calls = [
        call("\nThe tool image [bold]" + test_tool_image + "[/bold] is not required by any Development Environment anymore."),
        call("[yellow]Couldn't delete " + test_tool_image + ", because doesn't exist.\n")
    ]
    mock_print.assert_has_calls(calls)
    mock_confirm.assert_called_once_with("Would you like to remove it?")
    mock_dev_env_local_setup.container_engine.remove.assert_called_once_with(test_tool_image)

@patch("dem.cli.command.delete_cmd.stderr.print")
@patch("dem.cli.command.delete_cmd.stdout.print")
@patch("dem.cli.command.delete_cmd.typer.confirm")
def test_try_to_delete_tool_image_APIError(mock_confirm, mock_stdout_print, mock_stderr_print):
    # Test setup
    test_tool_image = "not_required_tool_image_to_delete:latest"
    mock_dev_env_local_setup = MagicMock()
    mock_confirm.return_value = True
    mock_dev_env_local_setup.container_engine.remove.side_effect = docker.errors.APIError("dummy")

    # Run unit under test
    delete_cmd.try_to_delete_tool_image(test_tool_image, mock_dev_env_local_setup)

    # Check expectations
    mock_stdout_print.assert_called_once_with("\nThe tool image [bold]" + test_tool_image + "[/bold] is not required by any Development Environment anymore.")
    mock_confirm.assert_called_once_with("Would you like to remove it?")
    mock_dev_env_local_setup.container_engine.remove.assert_called_once_with(test_tool_image)
    mock_stderr_print.assert_called_once_with("[red]Error: " + test_tool_image + " is used by a container. Unable to remove it.\n")

@patch("dem.cli.command.delete_cmd.stdout.print")
@patch("dem.cli.command.delete_cmd.typer.confirm")
def test_try_to_delete_tool_image_success(mock_confirm, mock_print):
    # Test setup
    test_tool_image = "not_required_tool_image_to_delete:latest"
    mock_dev_env_local_setup = MagicMock()
    mock_confirm.return_value = True

    # Run unit under test
    delete_cmd.try_to_delete_tool_image(test_tool_image, mock_dev_env_local_setup)

    # Check expectations
    calls = [
        call("\nThe tool image [bold]" + test_tool_image + "[/bold] is not required by any Development Environment anymore."),
        call("[green]Successfully removed![/]\n")
    ]
    mock_print.assert_has_calls(calls)
    mock_confirm.assert_called_once_with("Would you like to remove it?")
    mock_dev_env_local_setup.container_engine.remove.assert_called_once_with(test_tool_image)

@patch("dem.cli.command.delete_cmd.stdout.print")
@patch("dem.cli.command.delete_cmd.typer.confirm")
def test_try_to_delete_tool_image_not_confirmed(mock_confirm, mock_print):
    # Test setup
    test_tool_image = "not_required_tool_image_to_delete:latest"
    mock_dev_env_local_setup = MagicMock()
    mock_confirm.return_value = False

    # Run unit under test
    delete_cmd.try_to_delete_tool_image(test_tool_image, mock_dev_env_local_setup)

    # Check expectations
    mock_print.assert_called_once_with("\nThe tool image [bold]" + test_tool_image + "[/bold] is not required by any Development Environment anymore.")
    mock_confirm.assert_called_once_with("Would you like to remove it?")
    mock_dev_env_local_setup.container_engine.remove.assert_not_called()

@patch("dem.cli.command.delete_cmd.try_to_delete_tool_image")
def test_remove_unused_tool_images(mock_try_to_delete_tool_image):
    # Test setup
    mock_dev_env1 = MagicMock()
    mock_dev_env2 = MagicMock()
    mock_deleted_dev_env = MagicMock()
    mock_dev_env1.tools = [
        {
            "type": "build_system",
            "image_name": "still_required_tool_image",
            "image_version": "latest"
        }
    ]
    mock_dev_env2.tools = mock_dev_env1.tools
    mock_deleted_dev_env.tools = [
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
        },
        {
            "type": "toolchain",
            "image_name": "not_required_tool_image_to_delete",
            "image_version": "latest"
        }
    ]
    mock_dev_env_local_setup = MagicMock()
    mock_dev_env_local_setup.dev_envs = [mock_dev_env1, mock_dev_env2]

    # Run unit under test
    delete_cmd.remove_unused_tool_images(mock_deleted_dev_env, mock_dev_env_local_setup)

    # Check expectations
    calls = [
        call("not_required_tool_image_to_delete:latest", mock_dev_env_local_setup),
        call("not_required_tool_image_to_keep:latest", mock_dev_env_local_setup)
    ]
    mock_try_to_delete_tool_image.assert_has_calls(calls, any_order=True)


@patch("dem.cli.command.delete_cmd.remove_unused_tool_images")
@patch("dem.cli.command.delete_cmd.DevEnvLocalSetup")
def test_delete_dev_env_valid_name(mock_DevEnvLocalSetup, mock_remove_unused_tool_images):
    # Test setup
    fake_dev_env1 = MagicMock()
    fake_dev_env_to_delete = MagicMock()
    fake_dev_env_to_delete.name = "dev_env"
    fake_dev_env_local_setup = MagicMock()
    fake_dev_env_local_setup.dev_envs = [fake_dev_env1, fake_dev_env_to_delete]
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env_local_setup.get_dev_env_by_name.return_value = fake_dev_env_to_delete
    
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["delete", fake_dev_env_to_delete.name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_DevEnvLocalSetup.assert_called_once()
    fake_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(fake_dev_env_to_delete.name)
    fake_dev_env_local_setup.update_json.assert_called_once()
    mock_remove_unused_tool_images.assert_called_once_with(fake_dev_env_to_delete,
                                                           fake_dev_env_local_setup)

    assert fake_dev_env1 in fake_dev_env_local_setup.dev_envs
    assert fake_dev_env_to_delete not in fake_dev_env_local_setup.dev_envs

@patch("dem.cli.command.delete_cmd.stderr.print")
@patch("dem.cli.command.delete_cmd.DevEnvLocalSetup")
def test_delete_dev_env_invalid_name(mock_DevEnvLocalSetup, mock_stderr_print):
    # Test setup
    fake_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env_local_setup.get_dev_env_by_name.return_value = None
    test_invalid_name = "test_invalid_name"
    
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["delete", test_invalid_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_DevEnvLocalSetup.assert_called_once()
    fake_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(test_invalid_name)
    mock_stderr_print.assert_called_once_with("[red]Error: The [bold]" + test_invalid_name + "[/bold] Development Environment doesn't exist.")