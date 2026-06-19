"""Unit tests for DevEnv."""

import json

import dem.core.dev_env as dev_env

from unittest.mock import MagicMock

import pytest


def make_hosts() -> MagicMock:
    local_host = MagicMock()
    local_host.name = "local"
    local_host.container_engine = MagicMock()

    remote_host = MagicMock()
    remote_host.name = "remote"
    remote_host.container_engine = MagicMock()

    hosts = MagicMock()
    hosts.local = local_host
    hosts.remotes = {"remote": remote_host}
    return hosts


def make_descriptor() -> dict:
    return {
        "name": "test-dev-env",
        "installed": "True",
        "tools": [{"image_name": "tool", "image_version": "1.0"}],
        "custom_tasks": {"lint": "make lint"},
        "docker_tasks": [
            {
                "name": "build",
                "host_name": "local",
                "rm": True,
                "mount_workdir": False,
                "connect_to_network": True,
                "extra_args": "",
                "image": "tool:1.0",
                "command": "make",
                "enable_api": False,
            }
        ],
        "run_tasks_as_current_user": True,
        "enable_docker_network": True,
    }


def test_dev_env_initializes_tasks_and_flags() -> None:
    descriptor = make_descriptor()

    actual = dev_env.DevEnv(descriptor, make_hosts())

    assert actual.name == "test-dev-env"
    assert actual.custom_tasks == {"lint": "make lint"}
    assert actual.is_installed is True
    assert actual.enable_docker_network is True
    assert list(actual.tasks) == ["build"]
    assert actual.tasks["build"].network == "test-dev-env"
    assert actual.tasks["build"].run_as_current_user is True


def test_from_descriptor_path_loads_descriptor(tmp_path) -> None:
    descriptor_path = tmp_path / "dev_env_descriptor.json"
    descriptor_path.write_text(json.dumps(make_descriptor()))

    actual = dev_env.DevEnv.from_descriptor_path(str(descriptor_path), make_hosts())

    assert actual.name == "test-dev-env"
    assert list(actual.tasks) == ["build"]


def test_from_descriptor_path_raises_when_missing() -> None:
    with pytest.raises(FileNotFoundError):
        dev_env.DevEnv.from_descriptor_path("/missing/dev_env_descriptor.json", make_hosts())


def test_assign_tool_image_instances_uses_existing_or_placeholder() -> None:
    actual = dev_env.DevEnv(make_descriptor(), make_hosts())
    existing_tool_image = MagicMock()
    existing_tool_image.name = "tool:1.0"
    tool_images = MagicMock()
    tool_images.all_tool_images = {"tool:1.0": existing_tool_image}

    actual.assign_tool_image_instances(tool_images)

    assert actual.assigned_tool_images == {"tool:1.0": existing_tool_image}


def test_add_and_delete_task() -> None:
    actual = dev_env.DevEnv(make_descriptor(), make_hosts())

    actual.add_task("test", "echo hi")
    actual.del_task("test")

    assert "test" not in actual.custom_tasks


def test_del_task_raises_for_unknown_task() -> None:
    actual = dev_env.DevEnv(make_descriptor(), make_hosts())

    with pytest.raises(KeyError) as exc_info:
        actual.del_task("missing")

    assert str(exc_info.value) == "'Task [bold]missing[/] not found.'"


def test_is_installation_correct_checks_each_task_host() -> None:
    hosts = make_hosts()
    hosts.local.container_engine.get_local_tool_images.return_value = ["tool:1.0"]
    actual = dev_env.DevEnv(make_descriptor(), hosts)

    assert actual.is_installation_correct() is True

    hosts.local.container_engine.get_local_tool_images.return_value = []
    assert actual.is_installation_correct() is False


def test_get_deserialized_and_export(tmp_path) -> None:
    actual = dev_env.DevEnv(make_descriptor(), make_hosts())
    export_path = tmp_path / "export.json"

    serialized = actual.get_deserialized(omit_is_installed=True)
    actual.export(str(export_path))

    assert "installed" not in serialized
    assert json.loads(export_path.read_text()) == serialized


def test_start_engines_collects_failed_hosts() -> None:
    hosts = make_hosts()
    hosts.local.container_engine.start.side_effect = dev_env.ContainerEngineError("boom")
    actual = dev_env.DevEnv(make_descriptor(), hosts)

    with pytest.raises(dev_env.DevEnvError) as exc_info:
        actual.start_engines()

    assert (
        str(exc_info.value)
        == "Development Environment error: Failed to start the container engine on the following hosts: ['local']"
    )
