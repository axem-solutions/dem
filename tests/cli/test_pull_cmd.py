"""Tests for the pull CLI command."""
# tests/cli/test_pull_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

from rich.console import Console
import io
from dem.core.tool_images import ToolImages

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test helpers
## Test cases

@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvOrgSetup")
def test_dev_env_not_available_in_org(mock_DevEnvOrgSetup):
    # Test setup
    fake_dev_env_org_setup = MagicMock()
    mock_DevEnvOrgSetup.return_value = fake_dev_env_org_setup
    fake_dev_env_org_setup.get_dev_env_by_name.return_value = None

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["pull", "not existing env"], color=True)

    # Check expectations
    mock_DevEnvOrgSetup.assert_called_once()
    fake_dev_env_org_setup.get_dev_env_by_name.assert_called_once_with("not existing env")

    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[red]Error: The input Development Environment is not available for the organization.[/]")
    assert console.file.getvalue() == runner_result.stderr

@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvOrgSetup")
@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvLocalSetup")
def test_dev_env_already_installed(mock_DevEnvLocalSetup, mock_DevEnvOrgSetup):
    # Test setup
    fake_tools = MagicMock()
    fake_dev_env_org_setup = MagicMock()
    mock_DevEnvOrgSetup.return_value = fake_dev_env_org_setup
    fake_dev_env_org = MagicMock()
    # Set the same fake tools for both the local and org instance
    fake_dev_env_org.tools = fake_tools
    fake_dev_env_org_setup.get_dev_env_by_name.return_value = fake_dev_env_org

    fake_local_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_local_platform
    fake_dev_env_local = MagicMock()
    # Set the same fake tools for both the local and org instance
    fake_dev_env_local.tools = fake_tools
    fake_dev_env_local.name = "test_env"
    fake_dev_env_org.get_local_instance.return_value = fake_dev_env_local

    def stub_check_image_availability(*args, **kwargs):
        image_statuses = []
        for tool in fake_dev_env_local.tools:
            tool["image_status"] = ToolImages.LOCAL_AND_REGISTRY
            image_statuses.append(ToolImages.LOCAL_AND_REGISTRY)
        return image_statuses
    fake_dev_env_local.check_image_availability.side_effect = stub_check_image_availability

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["pull", "test_env"], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_DevEnvOrgSetup.assert_called_once()
    fake_dev_env_org_setup.get_dev_env_by_name.assert_called_once_with("test_env")

    mock_DevEnvLocalSetup.assert_called_once()
    fake_dev_env_org.get_local_instance.assert_called_once_with(fake_local_platform)
    fake_local_platform.pull_images.assert_called_once_with(fake_dev_env_local.tools)
    calls = [call(fake_local_platform.tool_images), 
             call(fake_local_platform.tool_images, update_tool_images=True)]
    fake_dev_env_local.check_image_availability.assert_has_calls(calls)

    console = Console(file=io.StringIO())
    console.print("The [yellow]test_env[/] Development Environment is ready!")
    assert console.file.getvalue() == runner_result.stdout

@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvOrgSetup")
@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvLocalSetup")
def test_dev_env_installed_but_different(mock_DevEnvLocalSetup,
                                         mock_DevEnvOrgSetup):
    # Test setup
    fake_tools = MagicMock()
    fake_dev_env_org_setup = MagicMock()
    mock_DevEnvOrgSetup.return_value = fake_dev_env_org_setup
    fake_dev_env_org = MagicMock()
    # Set the same fake tools for both the local and org instance
    fake_dev_env_org.tools = fake_tools
    fake_dev_env_org_setup.get_dev_env_by_name.return_value = fake_dev_env_org

    fake_local_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_local_platform
    fake_dev_env_local = MagicMock()
    fake_dev_env_local.name = "test_env"
    fake_dev_env_org.get_local_instance.return_value = fake_dev_env_local

    def stub_check_image_availability(*args, **kwargs):
        image_statuses = []
        for tool in fake_dev_env_local.tools:
            tool["image_status"] = ToolImages.LOCAL_AND_REGISTRY
            image_statuses.append(ToolImages.LOCAL_AND_REGISTRY)
        return image_statuses
    fake_dev_env_local.check_image_availability.side_effect = stub_check_image_availability

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["pull", "test_env"], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_DevEnvOrgSetup.assert_called_once()
    fake_dev_env_org_setup.get_dev_env_by_name.assert_called_once_with("test_env")

    mock_DevEnvLocalSetup.assert_called_once()
    fake_dev_env_org.get_local_instance.assert_called_once_with(fake_local_platform)

    assert fake_dev_env_local.tools == fake_dev_env_org.tools
    fake_local_platform.flush_to_file.assert_called_once()
    fake_local_platform.pull_images.assert_called_once_with(fake_dev_env_local.tools)

    calls = [call(fake_local_platform.tool_images), 
             call(fake_local_platform.tool_images, update_tool_images=True)]
    fake_dev_env_local.check_image_availability.assert_has_calls(calls)

    console = Console(file=io.StringIO())
    console.print("The [yellow]test_env[/] Development Environment is ready!")
    assert console.file.getvalue() == runner_result.stdout

@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvLocal")
@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvOrgSetup")
@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvLocalSetup")
def test_dev_env_new_install(mock_DevEnvLocalSetup, mock_DevEnvOrgSetup, mock_DevEnvLocal):
    # Test setup
    fake_dev_env_org_setup = MagicMock()
    mock_DevEnvOrgSetup.return_value = fake_dev_env_org_setup
    fake_dev_env_org = MagicMock()
    # Set the same fake tools for both the local and org instance
    fake_dev_env_org_setup.get_dev_env_by_name.return_value = fake_dev_env_org

    fake_local_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_local_platform
    fake_dev_env_org.get_local_instance.return_value = None

    fake_dev_env_local = MagicMock()
    fake_dev_env_local.name = "test_env"
    mock_DevEnvLocal.return_value = fake_dev_env_local

    fake_dev_env_local.tools = MagicMock()
    fake_dev_env_local.check_image_availability.return_value = [ToolImages.LOCAL_AND_REGISTRY] * 3

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["pull", "test_env"], color=True)

    # Check expectations
    mock_DevEnvOrgSetup.assert_called_once()
    fake_dev_env_org_setup.get_dev_env_by_name.assert_called_once_with("test_env")

    mock_DevEnvLocalSetup.assert_called_once()
    fake_dev_env_org.get_local_instance.assert_called_once_with(fake_local_platform)

    mock_DevEnvLocal.assert_called_once_with(dev_env_org=fake_dev_env_org)
    fake_local_platform.dev_envs.append.assert_called_once_with(fake_dev_env_local)
    fake_local_platform.flush_to_file.assert_called_once()

    fake_local_platform.pull_images.assert_called_once_with(fake_dev_env_local.tools)

    calls = [call(fake_local_platform.tool_images), 
             call(fake_local_platform.tool_images, update_tool_images=True)]
    fake_dev_env_local.check_image_availability.assert_has_calls(calls)
    
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("The [yellow]test_env[/] Development Environment is ready!")
    assert console.file.getvalue() == runner_result.stdout