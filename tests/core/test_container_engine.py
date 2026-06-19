"""Unit tests for the container engine."""

import docker.errors
import dem.core.container_engine as container_engine

from unittest.mock import MagicMock, patch

import pytest


class MockImage:
    def __init__(self, tags: list[str]) -> None:
        self.tags = tags


@patch("dem.core.container_engine.DockerClient")
def test_start_creates_client(mock_docker_client_class: MagicMock) -> None:
    engine = container_engine.ContainerEngine("unix://var/run/docker.sock")

    engine.start()

    mock_docker_client_class.assert_called_once_with(
        base_url="unix://var/run/docker.sock", version="auto"
    )
    assert engine._docker_client is mock_docker_client_class.return_value


@patch("dem.core.container_engine.DockerClient")
def test_start_raises_on_docker_exception(mock_docker_client_class: MagicMock) -> None:
    mock_docker_client_class.side_effect = docker.errors.DockerException("boom")
    engine = container_engine.ContainerEngine("tcp://docker")

    with pytest.raises(container_engine.ContainerEngineError) as exc_info:
        engine.start()

    assert str(exc_info.value) == "Container engine error: Unable to connect to the Docker Engine: boom"


def test_get_local_tool_images_returns_all_non_empty_tags() -> None:
    engine = container_engine.ContainerEngine("tcp://docker")
    engine._docker_client = MagicMock()
    engine._docker_client.images.list.return_value = [
        MockImage(["alpine:latest"]),
        MockImage([""]),
        MockImage(["tool:1.0", "tool:latest"]),
    ]

    assert engine.get_local_tool_images() == ["alpine:latest", "tool:1.0", "tool:latest"]


@patch.object(container_engine.Core, "user_output")
def test_pull_streams_progress(mock_user_output: MagicMock) -> None:
    engine = container_engine.ContainerEngine("tcp://docker")
    engine._docker_client = MagicMock()
    response = MagicMock()
    engine._docker_client.api.pull.return_value = response

    engine.pull("test/image:latest")

    engine._docker_client.api.pull.assert_called_once_with(
        "test/image:latest", stream=True, decode=True
    )
    mock_user_output.progress_generator.assert_called_once_with(response)


@patch.object(container_engine.Core, "user_output")
def test_run_streams_logs_and_removes_container(mock_user_output: MagicMock) -> None:
    engine = container_engine.ContainerEngine("tcp://docker")
    engine._docker_client = MagicMock()
    container = MagicMock()
    container.logs.return_value = [b"log one\n", b"log two\n"]
    engine._docker_client.containers.run.return_value = container

    engine.run("test/image:latest", "echo hi", remove=True, name="task")

    engine._docker_client.containers.run.assert_called_once_with(
        "test/image:latest",
        "echo hi",
        detach=True,
        stdout=True,
        stderr=True,
        name="task",
    )
    mock_user_output.msg.assert_any_call("log one")
    mock_user_output.msg.assert_any_call("log two")
    container.remove.assert_called_once()


def test_run_keeps_container_when_remove_is_false() -> None:
    engine = container_engine.ContainerEngine("tcp://docker")
    engine._docker_client = MagicMock()
    container = MagicMock()
    container.logs.return_value = []
    engine._docker_client.containers.run.return_value = container

    engine.run("test/image:latest", remove=False)

    container.remove.assert_not_called()


@patch.object(container_engine.Core, "user_output")
def test_remove_handles_missing_image(mock_user_output: MagicMock) -> None:
    engine = container_engine.ContainerEngine("tcp://docker")
    engine._docker_client = MagicMock()
    engine._docker_client.images.remove.side_effect = docker.errors.ImageNotFound("missing")

    engine.remove("test/image:latest")

    mock_user_output.msg.assert_called_once_with(
        "[yellow]The test/image:latest doesn't exist. Unable to remove it.[/]\n"
    )


def test_remove_raises_on_api_error() -> None:
    engine = container_engine.ContainerEngine("tcp://docker")
    engine._docker_client = MagicMock()
    engine._docker_client.images.remove.side_effect = docker.errors.APIError("busy")

    with pytest.raises(container_engine.ContainerEngineError) as exc_info:
        engine.remove("test/image:latest")

    assert (
        str(exc_info.value)
        == "Container engine error: The test/image:latest is used by a container. Unable to remove it.\n"
    )


def test_create_network() -> None:
    engine = container_engine.ContainerEngine("tcp://docker")
    engine._docker_client = MagicMock()

    engine.create_network("test-network")

    engine._docker_client.networks.create.assert_called_once_with("test-network")


@patch.object(container_engine.Core, "user_output")
def test_remove_network_handles_missing_network(mock_user_output: MagicMock) -> None:
    engine = container_engine.ContainerEngine("tcp://docker")
    engine._docker_client = MagicMock()
    engine._docker_client.networks.get.side_effect = docker.errors.NotFound("missing")

    engine.remove_network("test-network")

    mock_user_output.msg.assert_called_once_with(
        "[yellow]The test-network doesn't exist. Unable to remove it.[/]\n"
    )
