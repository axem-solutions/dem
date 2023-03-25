"""Tests for the pull CLI command."""
# tests/cli/test_pull_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

from rich.console import Console
import io
import dem.core.dev_env_setup as dev_env_setup

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test helpers
## Test cases

@patch("dem.cli.command.pull_cmd.data_management.read_deserialized_dev_env_org_json")
@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvOrgSetup")
def test_dev_env_not_available_in_org(mock_DevEnvOrgSetup, mock_read_deserialized_dev_env_org_json):
    # Test setup
    fake_deserialized_dev_env_org_json = MagicMock()
    mock_read_deserialized_dev_env_org_json.return_value = fake_deserialized_dev_env_org_json
    fake_dev_env_org_setup = MagicMock()
    mock_DevEnvOrgSetup.return_value = fake_dev_env_org_setup
    fake_dev_env_org_setup.get_dev_env.return_value = None

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["pull", "not existing env"], color=True)

    mock_read_deserialized_dev_env_org_json.assert_called_once()
    mock_DevEnvOrgSetup.assert_called_once_with(fake_deserialized_dev_env_org_json)
    fake_dev_env_org_setup.get_dev_env.assert_called_once_with("not existing env")

    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[red]Error: The input Development Environment is not available for the organization.[/]")
    assert console.file.getvalue() == runner_result.stderr

@patch("dem.cli.command.pull_cmd.registry.list_repos")
@patch("dem.cli.command.pull_cmd.container_engine.ContainerEngine")
@patch("dem.cli.command.pull_cmd.data_management.read_deserialized_dev_env_org_json")
@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvOrgSetup")
@patch("dem.cli.command.pull_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvLocalSetup")
def test_dev_env_already_installed(mock_DevEnvLocalSetup, mock_read_deserialized_dev_env_local_json, 
                                   mock_DevEnvOrgSetup, mock_read_deserialized_dev_env_org_json,
                                   mock_ContainerEngine, mock_list_repos):
    # Test setup
    fake_tools = MagicMock()
    fake_deserialized_dev_env_org_json = MagicMock()
    mock_read_deserialized_dev_env_org_json.return_value = fake_deserialized_dev_env_org_json
    fake_dev_env_org_setup = MagicMock()
    mock_DevEnvOrgSetup.return_value = fake_dev_env_org_setup
    fake_dev_env_org = MagicMock()
    # Set the same fake tools for both the local and org instance
    fake_dev_env_org.tools = fake_tools
    fake_dev_env_org_setup.get_dev_env.return_value = fake_dev_env_org

    fake_deserialized_dev_env_local_json = MagicMock()
    mock_read_deserialized_dev_env_local_json.return_value = fake_deserialized_dev_env_local_json
    fake_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env_local = MagicMock()
    # Set the same fake tools for both the local and org instance
    fake_dev_env_local.tools = fake_tools
    fake_dev_env_local.name = "test_env"
    fake_dev_env_org.get_local_instance.return_value = fake_dev_env_local

    fake_container_engine = MagicMock()
    mock_ContainerEngine.return_value = fake_container_engine
    fake_local_images = MagicMock()
    fake_container_engine.get_local_tool_images.return_value = fake_local_images
    fake_registry_images = MagicMock()
    mock_list_repos.return_value = fake_registry_images
    fake_image_statuses = [dev_env_setup.IMAGE_LOCAL_AND_REGISTRY] * 5
    fake_dev_env_local.check_image_availability.return_value = fake_image_statuses

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["pull", "test_env"], color=True)

    mock_read_deserialized_dev_env_org_json.assert_called_once()
    mock_DevEnvOrgSetup.assert_called_once_with(fake_deserialized_dev_env_org_json)
    fake_dev_env_org_setup.get_dev_env.assert_called_once_with("test_env")

    mock_read_deserialized_dev_env_local_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_deserialized_dev_env_local_json)
    fake_dev_env_org.get_local_instance.assert_called_once_with(fake_dev_env_local_setup)

    mock_ContainerEngine.assert_called_once()
    fake_container_engine.get_local_tool_images.assert_called()
    mock_list_repos.assert_called_once()
    fake_dev_env_local.check_image_availability.assert_called_with(fake_local_images, 
                                                                   fake_registry_images)
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("The [yellow]test_env[/] Development Environment is ready!")
    assert console.file.getvalue() == runner_result.stdout

@patch("dem.cli.command.pull_cmd.data_management.write_deserialized_dev_env_json")
@patch("dem.cli.command.pull_cmd.registry.list_repos")
@patch("dem.cli.command.pull_cmd.container_engine.ContainerEngine")
@patch("dem.cli.command.pull_cmd.data_management.read_deserialized_dev_env_org_json")
@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvOrgSetup")
@patch("dem.cli.command.pull_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvLocalSetup")
def test_dev_env_installed_but_different(mock_DevEnvLocalSetup,
                                         mock_read_deserialized_dev_env_local_json, 
                                         mock_DevEnvOrgSetup, 
                                         mock_read_deserialized_dev_env_org_json,
                                         mock_ContainerEngine, mock_list_repos,
                                         mock_write_deserialized_dev_env_local_json):
    # Test setup
    fake_tools = MagicMock()
    fake_deserialized_dev_env_org_json = MagicMock()
    mock_read_deserialized_dev_env_org_json.return_value = fake_deserialized_dev_env_org_json
    fake_dev_env_org_setup = MagicMock()
    mock_DevEnvOrgSetup.return_value = fake_dev_env_org_setup
    fake_dev_env_org = MagicMock()
    # Set the same fake tools for both the local and org instance
    fake_dev_env_org.tools = fake_tools
    fake_dev_env_org_setup.get_dev_env.return_value = fake_dev_env_org

    fake_deserialized_dev_env_local_json = MagicMock()
    mock_read_deserialized_dev_env_local_json.return_value = fake_deserialized_dev_env_local_json
    fake_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env_local = MagicMock()
    fake_dev_env_local.name = "test_env"
    fake_dev_env_org.get_local_instance.return_value = fake_dev_env_local

    fake_dev_env_local_setup.get_deserialized.return_value = fake_deserialized_dev_env_local_json

    fake_container_engine = MagicMock()
    mock_ContainerEngine.return_value = fake_container_engine
    fake_local_images = MagicMock()
    fake_container_engine.get_local_tool_images.return_value = fake_local_images
    fake_registry_images = MagicMock()
    mock_list_repos.return_value = fake_registry_images
    fake_image_statuses = [dev_env_setup.IMAGE_LOCAL_AND_REGISTRY] * 5
    fake_dev_env_local.check_image_availability.return_value = fake_image_statuses

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["pull", "test_env"], color=True)

    mock_read_deserialized_dev_env_org_json.assert_called_once()
    mock_DevEnvOrgSetup.assert_called_once_with(fake_deserialized_dev_env_org_json)
    fake_dev_env_org_setup.get_dev_env.assert_called_once_with("test_env")

    mock_read_deserialized_dev_env_local_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_deserialized_dev_env_local_json)
    fake_dev_env_org.get_local_instance.assert_called_once_with(fake_dev_env_local_setup)

    fake_dev_env_local_setup.dev_envs.remove.assert_called_once_with(fake_dev_env_local)
    assert fake_dev_env_local.tools == fake_dev_env_org.tools
    fake_dev_env_local_setup.dev_envs.append.assert_called_once_with(fake_dev_env_local)
    fake_dev_env_local_setup.get_deserialized.assert_called_once()
    mock_write_deserialized_dev_env_local_json.assert_called_once_with(fake_deserialized_dev_env_local_json)

    mock_ContainerEngine.assert_called_once()
    fake_container_engine.get_local_tool_images.assert_called()
    mock_list_repos.assert_called_once()
    fake_dev_env_local.check_image_availability.assert_called_with(fake_local_images, 
                                                                   fake_registry_images)
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("The [yellow]test_env[/] Development Environment is ready!")
    assert console.file.getvalue() == runner_result.stdout

@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvLocal")
@patch("dem.cli.command.pull_cmd.data_management.write_deserialized_dev_env_json")
@patch("dem.cli.command.pull_cmd.registry.list_repos")
@patch("dem.cli.command.pull_cmd.container_engine.ContainerEngine")
@patch("dem.cli.command.pull_cmd.data_management.read_deserialized_dev_env_org_json")
@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvOrgSetup")
@patch("dem.cli.command.pull_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.pull_cmd.dev_env_setup.DevEnvLocalSetup")
def test_dev_env_new_install(mock_DevEnvLocalSetup, mock_read_deserialized_dev_env_local_json, 
                             mock_DevEnvOrgSetup, mock_read_deserialized_dev_env_org_json,
                             mock_ContainerEngine, mock_list_repos,
                             mock_write_deserialized_dev_env_local_json, mock_DevEnvLocal):
    # Test setup
    fake_deserialized_dev_env_org_json = MagicMock()
    mock_read_deserialized_dev_env_org_json.return_value = fake_deserialized_dev_env_org_json
    fake_dev_env_org_setup = MagicMock()
    mock_DevEnvOrgSetup.return_value = fake_dev_env_org_setup
    fake_dev_env_org = MagicMock()
    # Set the same fake tools for both the local and org instance
    fake_dev_env_org_setup.get_dev_env.return_value = fake_dev_env_org

    fake_deserialized_dev_env_local_json = MagicMock()
    mock_read_deserialized_dev_env_local_json.return_value = fake_deserialized_dev_env_local_json
    fake_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env_org.get_local_instance.return_value = None

    fake_dev_env_local = MagicMock()
    fake_dev_env_local.name = "test_env"
    mock_DevEnvLocal.return_value = fake_dev_env_local
    fake_dev_env_local_setup.get_deserialized.return_value = fake_deserialized_dev_env_local_json

    fake_container_engine = MagicMock()
    mock_ContainerEngine.return_value = fake_container_engine
    fake_local_images = MagicMock()
    fake_container_engine.get_local_tool_images.return_value = fake_local_images
    fake_registry_images = MagicMock()
    mock_list_repos.return_value = fake_registry_images
    fake_image_statuses = [dev_env_setup.IMAGE_LOCAL_AND_REGISTRY] * 5
    fake_dev_env_local.check_image_availability.return_value = fake_image_statuses

    fake_tools = [
        {
            "image_status": dev_env_setup.IMAGE_REGISTRY_ONLY,
            "image_name": "registry_only_tool1",
            "image_version": "latest"
        },
        {
            "image_status": dev_env_setup.IMAGE_REGISTRY_ONLY,
            "image_name": "registry_only_tool2",
            "image_version": "latest"
        },
        {
            "image_status": dev_env_setup.IMAGE_LOCAL_AND_REGISTRY,
            "image_name": "already_available_tool",
            "image_version": "latest"
        }
    ]
    fake_dev_env_local.tools = fake_tools

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["pull", "test_env"], color=True)

    mock_read_deserialized_dev_env_org_json.assert_called_once()
    mock_DevEnvOrgSetup.assert_called_once_with(fake_deserialized_dev_env_org_json)
    fake_dev_env_org_setup.get_dev_env.assert_called_once_with("test_env")

    mock_read_deserialized_dev_env_local_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_deserialized_dev_env_local_json)
    fake_dev_env_org.get_local_instance.assert_called_once_with(fake_dev_env_local_setup)

    mock_DevEnvLocal.assert_called_once_with(dev_env_org=fake_dev_env_org)
    fake_dev_env_local_setup.dev_envs.append.assert_called_once_with(fake_dev_env_local)
    fake_dev_env_local_setup.get_deserialized.assert_called_once()
    mock_write_deserialized_dev_env_local_json.assert_called_once_with(fake_deserialized_dev_env_local_json)

    mock_ContainerEngine.assert_called_once()
    fake_container_engine.get_local_tool_images.assert_called()
    mock_list_repos.assert_called_once()
    fake_dev_env_local.check_image_availability.assert_called_with(fake_local_images, 
                                                                   fake_registry_images)

    calls = [call("registry_only_tool1:latest"), call("registry_only_tool2:latest")]
    fake_container_engine.pull.assert_has_calls(calls)
    
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("Pulling image: registry_only_tool1:latest")
    console.print("Pulling image: registry_only_tool2:latest")
    console.print("The [yellow]test_env[/] Development Environment is ready!")
    assert console.file.getvalue() == runner_result.stdout