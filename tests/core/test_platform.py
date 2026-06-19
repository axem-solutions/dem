"""Unit tests for Platform."""

import dem.core.platform as platform

from unittest.mock import MagicMock, patch

import pytest


@patch.object(platform.Core, "config_file")
@patch("dem.core.platform.APIServer")
@patch("dem.core.platform.Hosts")
@patch("dem.core.platform.LocalDevEnvJSON")
@patch("dem.core.platform.DevEnv")
def test_load_dev_envs_sets_version_and_builds_dev_envs(
    mock_dev_env_class: MagicMock,
    mock_local_dev_env_json_class: MagicMock,
    mock_hosts_class: MagicMock,
    mock_api_server_class: MagicMock,
    mock_config_file: MagicMock,
) -> None:
    mock_local_dev_env_json = MagicMock()
    mock_local_dev_env_json.deserialized = {
        "version": "0.1",
        "default_dev_env": "demo",
        "development_environments": [{"name": "demo"}],
    }
    mock_local_dev_env_json_class.return_value = mock_local_dev_env_json
    actual = platform.Platform()

    actual.load_dev_envs()

    assert actual.version == "0.1"
    assert actual.default_dev_env_name == "demo"
    assert actual.local_dev_envs == [mock_dev_env_class.return_value]
    mock_dev_env_class.assert_called_once_with({"name": "demo"}, mock_hosts_class.return_value)


@patch("dem.core.platform.ToolImages")
@patch.object(platform.Platform, "__init__", return_value=None)
def test_tool_images_uses_local_host_engine(
    mock_init: MagicMock, mock_tool_images_class: MagicMock
) -> None:
    actual = platform.Platform()
    actual.hosts = MagicMock()
    actual.hosts.local.container_engine = MagicMock()
    actual._tool_images = None
    actual._registries = MagicMock()
    actual.get_tool_image_info_from_registries = False

    tool_images = actual.tool_images

    assert tool_images is mock_tool_images_class.return_value
    mock_tool_images_class.assert_called_once_with(
        actual.hosts.local.container_engine, actual._registries
    )
    tool_images.update.assert_called_once_with(True, False)


@patch("dem.core.platform.DevEnvCatalogs")
@patch.object(platform.Platform, "__init__", return_value=None)
def test_dev_env_catalogs_uses_hosts(
    mock_init: MagicMock, mock_catalogs_class: MagicMock
) -> None:
    actual = platform.Platform()
    actual.hosts = MagicMock()
    actual._dev_env_catalogs = None

    catalogs = actual.dev_env_catalogs

    assert catalogs is mock_catalogs_class.return_value
    mock_catalogs_class.assert_called_once_with(actual.hosts)


@patch.object(platform.Platform, "__init__", return_value=None)
def test_get_deserialized_and_get_dev_env_by_name(mock_init: MagicMock) -> None:
    actual = platform.Platform()
    actual.version = "0.1"
    actual.default_dev_env_name = "demo"
    matching_dev_env = MagicMock()
    matching_dev_env.name = "demo"
    matching_dev_env.get_deserialized.return_value = {"name": "demo"}
    actual.local_dev_envs = [matching_dev_env]

    assert actual.get_deserialized() == {
        "version": "0.1",
        "default_dev_env": "demo",
        "development_environments": [{"name": "demo"}],
    }
    assert actual.get_dev_env_by_name("demo") is matching_dev_env
    assert actual.get_dev_env_by_name("missing") is None


@patch.object(platform.Platform, "flush_dev_env_properties")
@patch.object(platform.Platform, "__init__", return_value=None)
def test_install_dev_env_pulls_images_per_task_and_network(
    mock_init: MagicMock, mock_flush: MagicMock
) -> None:
    actual = platform.Platform()
    actual.user_output = MagicMock()
    actual.hosts = MagicMock()
    task = MagicMock()
    task.image = "tool:1.0"
    task.host_name = "remote-a"
    dev_env = MagicMock()
    dev_env.tasks = {"build": task}
    tool_image = MagicMock()
    tool_image.name = "tool:1.0"
    dev_env.assigned_tool_images = {"tool:1.0": tool_image}
    dev_env.enable_docker_network = True
    dev_env.name = "demo"
    host = MagicMock()
    actual.hosts.get_host_by_name.return_value = host
    actual.hosts.local.container_engine = MagicMock()

    actual.install_dev_env(dev_env)

    host.container_engine.pull.assert_called_once_with("tool:1.0")
    actual.hosts.local.container_engine.create_network.assert_called_once_with("demo")
    assert dev_env.is_installed is True
    mock_flush.assert_called_once()


@patch.object(platform.Platform, "flush_dev_env_properties")
@patch.object(platform.Platform, "__init__", return_value=None)
def test_uninstall_dev_env_keeps_shared_images_and_clears_default(
    mock_init: MagicMock, mock_flush: MagicMock
) -> None:
    actual = platform.Platform()
    actual.are_tool_images_assigned = True
    actual.hosts = MagicMock()
    actual.hosts.local.container_engine = MagicMock()
    actual.default_dev_env_name = "demo"
    shared_host = MagicMock()
    shared_host.name = "remote-a"
    shared_host.container_engine = MagicMock()

    shared_task = MagicMock()
    shared_task.host = shared_host
    shared_task.image = "shared:1.0"

    removable_task = MagicMock()
    removable_task.host = shared_host
    removable_task.image = "unique:1.0"

    other_dev_env = MagicMock()
    other_dev_env.is_installed = True
    other_dev_env.tasks = {"build": shared_task}

    dev_env_to_uninstall = MagicMock()
    dev_env_to_uninstall.is_installed = True
    dev_env_to_uninstall.tasks = {"shared": shared_task, "remove": removable_task}
    dev_env_to_uninstall.enable_docker_network = True
    dev_env_to_uninstall.name = "demo"

    actual.local_dev_envs = [dev_env_to_uninstall, other_dev_env]

    statuses = list(actual.uninstall_dev_env(dev_env_to_uninstall))

    assert statuses == ["The unique:1.0 image has been removed."]
    shared_host.container_engine.remove.assert_called_once_with("unique:1.0")
    actual.hosts.local.container_engine.remove_network.assert_called_once_with("demo")
    assert actual.default_dev_env_name == ""
    assert dev_env_to_uninstall.is_installed is False
    mock_flush.assert_called_once()


@patch("dem.core.platform.DevEnv.from_descriptor_path")
@patch.object(platform.Platform, "__init__", return_value=None)
def test_init_project_uses_hosts_when_loading_descriptor(
    mock_init: MagicMock, mock_from_descriptor_path: MagicMock, tmp_path
) -> None:
    project_path = tmp_path / "project"
    descriptor_dir = project_path / ".axem"
    descriptor_dir.mkdir(parents=True)
    (descriptor_dir / "dev_env_descriptor.json").write_text("{}")
    actual = platform.Platform()
    actual.hosts = MagicMock()
    actual._tool_images = MagicMock()
    actual.local_dev_envs = []
    actual.get_dev_env_by_name = MagicMock(return_value=None)

    actual.init_project(str(project_path))

    mock_from_descriptor_path.assert_called_once_with(
        f"{project_path}/.axem/dev_env_descriptor.json", actual.hosts
    )
    mock_from_descriptor_path.return_value.assign_tool_image_instances.assert_called_once_with(
        actual._tool_images
    )
    assert actual.local_dev_envs == [mock_from_descriptor_path.return_value]


@patch.object(platform.Core, "config_file")
@patch("dem.core.platform.APIServer")
@patch("dem.core.platform.Hosts")
@patch("dem.core.platform.LocalDevEnvJSON")
def test_load_dev_envs_raises_for_invalid_version(
    mock_local_dev_env_json_class: MagicMock,
    mock_hosts_class: MagicMock,
    mock_api_server_class: MagicMock,
    mock_config_file: MagicMock,
) -> None:
    mock_local_dev_env_json = MagicMock()
    mock_local_dev_env_json.deserialized = {"version": "1.0", "development_environments": []}
    mock_local_dev_env_json_class.return_value = mock_local_dev_env_json
    actual = platform.Platform()

    with pytest.raises(platform.DataStorageError):
        actual.load_dev_envs()
