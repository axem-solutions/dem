"""Unit test for the image_management."""
# tests/core/test_image_management.py

import dem.core.container_engine as container_engine
from unittest.mock import patch, MagicMock

import docker

class mockImage:
    def __init__(self, tags: list[str]) -> None:
        self.tags = tags

def _get_test_image_tags_as_images(test_image_tags):
    test_images = []
    for test_image_tag in test_image_tags:
        test_images.append(mockImage(test_image_tag))
    return test_images

@patch("docker.from_env")
def test_get_local_tool_images(mock_docker_from_env):
    test_image_tags = [
    ["alpine:latest"],
    [""],
    ["axemsolutions/make_gnu_arm:v1.0.0"],
    ["axemsolutions/stlink_org:latest", "axemsolutions/stlink_org:v1.0.0"],
    ["axemsolutions/cpputest:latest"],
    ["axemsolutions/make_gnu_arm:latest", "axemsolutions/make_gnu_arm:v0.1.0", "axemsolutions/make_gnu_arm:v1.1.0"],
    ["debian:latest"],
    ["ubuntu:latest"],
    ["hello-world:latest"],
    [""],
    ]
    expected_image_tags = [
    "axemsolutions/make_gnu_arm:v1.0.0",
    "axemsolutions/stlink_org:latest", 
    "axemsolutions/stlink_org:v1.0.0",
    "axemsolutions/cpputest:latest",
    "axemsolutions/make_gnu_arm:latest", 
    "axemsolutions/make_gnu_arm:v0.1.0", 
    "axemsolutions/make_gnu_arm:v1.1.0",
    ]
    mock_docker_client = MagicMock()
    mock_docker_client.images.list.return_value = _get_test_image_tags_as_images(test_image_tags)
    mock_docker_from_env.return_value = mock_docker_client

    container_engine_obj = container_engine.ContainerEngine()
    assert expected_image_tags == container_engine_obj.get_local_tool_images()

    mock_docker_from_env.assert_called_once()
    mock_docker_client.images.list.assert_called_once()

@patch("docker.from_env")
def test_get_local_tool_images_when_none_available(mock_docker_from_env):
    test_image_tags = []
    expected_image_tags = []
    mock_docker_client = MagicMock()
    mock_docker_from_env.return_value = mock_docker_client
    mock_docker_client.images.list.return_value = _get_test_image_tags_as_images(test_image_tags)

    container_engine_obj = container_engine.ContainerEngine()
    assert expected_image_tags == container_engine_obj.get_local_tool_images()

    mock_docker_from_env.assert_called_once()
    mock_docker_client.images.list.assert_called_once()