"""Unit test for the image_management."""
# tests/core/test_image_management.py

# Unit under test:
import dem.core.container_engine as container_engine

# Test framework
import pytest
from unittest.mock import patch, MagicMock, call

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
    # Test setup
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
    "alpine:latest",
    "axemsolutions/make_gnu_arm:v1.0.0",
    "axemsolutions/stlink_org:latest", 
    "axemsolutions/stlink_org:v1.0.0",
    "axemsolutions/cpputest:latest",
    "axemsolutions/make_gnu_arm:latest", 
    "axemsolutions/make_gnu_arm:v0.1.0", 
    "axemsolutions/make_gnu_arm:v1.1.0",
    "debian:latest",
    "ubuntu:latest",
    "hello-world:latest",
    ]
    mock_docker_client = MagicMock()
    mock_docker_client.images.list.return_value = _get_test_image_tags_as_images(test_image_tags)
    mock_docker_from_env.return_value = mock_docker_client

    # Run unit under test
    container_engine_obj = container_engine.ContainerEngine()
    actual_image_tags = container_engine_obj.get_local_tool_images()

    # Check expectations
    assert expected_image_tags == actual_image_tags

    mock_docker_from_env.assert_called_once()
    mock_docker_client.images.list.assert_called_once()

@patch("docker.from_env")
def test_get_local_tool_images_when_none_available(mock_docker_from_env):
    # Test setup
    test_image_tags = []
    expected_image_tags = []
    fake_docker_client = MagicMock()
    mock_docker_from_env.return_value = fake_docker_client
    fake_docker_client.images.list.return_value = _get_test_image_tags_as_images(test_image_tags)

    # Run unit under test
    container_engine_obj = container_engine.ContainerEngine()
    actual_image_tags = container_engine_obj.get_local_tool_images()

    # Check expectations
    assert expected_image_tags == actual_image_tags

    mock_docker_from_env.assert_called_once()
    fake_docker_client.images.list.assert_called_once()

@patch.object(container_engine.Core, "user_output")
@patch("dem.core.container_engine.docker.from_env")
def test_pull(mock_docker_from_env, mock_user_output):
    # Test setup
    mock_docker_client = MagicMock()
    mock_docker_from_env.return_value = mock_docker_client
    test_image_to_pull = "test_image:latest"
    mock_response = MagicMock()
    mock_docker_client.api.pull.return_value = mock_response

    test_container_engine = container_engine.ContainerEngine()

    # Run unit under test
    test_container_engine.pull(test_image_to_pull)

    # Check expectations
    mock_docker_from_env.assert_called_once()
    mock_docker_client.api.pull.assert_called_once_with(test_image_to_pull, stream=True, 
                                                        decode=True)
    mock_user_output.progress_generator.assert_called_once_with(mock_response)

@patch.object(container_engine.Core, "user_output")
@patch("docker.from_env")
def test_run(mock_from_env, mock_user_output):
    # Test setup
    test_container_arguments = [
        "-p", "8080:8080", "-p", "50000:50000", "--name", "jenkins", "--privileged", "--rm",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-v", "/home/murai/jenkins_home_axem:/var/jenkins_home", 
		"axemsolutions/jenkins:latest",
        "command1 command2"
    ]
    mock_docker_client = MagicMock()
    mock_from_env.return_value = mock_docker_client
    mock_run_result = MagicMock()
    mock_docker_client.containers.run.return_value = mock_run_result
    fake_log_lines = [
        b"log_line_1\n", 
        b"log_line_2\n",
    ]
    mock_run_result.logs.return_value = fake_log_lines

    test_container_engine = container_engine.ContainerEngine()

    # Run unit under test
    test_container_engine.run(test_container_arguments)

    # Check expectations
    mock_docker_client.containers.run.assert_called_once_with("axemsolutions/jenkins:latest", 
                                                              command="command1 command2", 
                                                              auto_remove=True, 
                                                              privileged=True,
                                                              volumes=[
                                                                "/var/run/docker.sock:/var/run/docker.sock",
                                                                "/home/murai/jenkins_home_axem:/var/jenkins_home"
                                                              ],
                                                              ports={
                                                                  "8080": 8080,
                                                                  "50000": 50000
                                                              },
                                                              name="jenkins",
                                                              stderr=True, 
                                                              detach=True)
    mock_run_result.logs.assert_called_once_with(stream=True)
    calls = [
        call("log_line_1"), 
        call("log_line_2"),
    ]
    mock_user_output.msg.assert_has_calls(calls)

@patch("docker.from_env")
def test_run_d(mock_from_env):
    # Test setup
    test_container_arguments = [
        "-p", "8080:8080", "-p", "50000:50000", "--name", "jenkins", "--privileged", "--rm", "-d",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-v", "/home/murai/jenkins_home_axem:/var/jenkins_home", 
		"axemsolutions/jenkins:latest",
        "command"
    ]
    mock_docker_client = MagicMock()
    mock_from_env.return_value = mock_docker_client

    test_container_engine = container_engine.ContainerEngine()

    # Run unit under test
    test_container_engine.run(test_container_arguments)

    # Check expectations
    mock_docker_client.containers.run.assert_called_once_with("axemsolutions/jenkins:latest", 
                                                              command="command", 
                                                              auto_remove=True, 
                                                              privileged=True,
                                                              volumes=[
                                                                "/var/run/docker.sock:/var/run/docker.sock",
                                                                "/home/murai/jenkins_home_axem:/var/jenkins_home"
                                                              ],
                                                              ports={
                                                                  "8080": 8080,
                                                                  "50000": 50000
                                                              },
                                                              name="jenkins",
                                                              stderr=True, 
                                                              detach=True)

@patch("docker.from_env")
def test_run_ValueError(mock_from_env):
    # Test setup
    test_container_arguments = [
        "-p", "80808080"
    ]
    mock_docker_client = MagicMock()
    mock_from_env.return_value = mock_docker_client

    test_container_engine = container_engine.ContainerEngine()

    with pytest.raises(container_engine.ContainerEngineError) as exported_exception_info:
        # Run unit under test
        test_container_engine.run(test_container_arguments)

        # Check expectations
        assert str(exported_exception_info) == "The option -p has invalid argument: 80808080"

@patch("docker.from_env")
def test_run_not_supported_param(mock_from_env):
    # Test setup
    test_container_arguments = [
        "-x", "80808080"
    ]
    mock_docker_client = MagicMock()
    mock_from_env.return_value = mock_docker_client

    test_container_engine = container_engine.ContainerEngine()

    with pytest.raises(container_engine.ContainerEngineError) as exported_exception_info:
        # Run unit under test
        test_container_engine.run(test_container_arguments)

        # Check expectations
        assert str(exported_exception_info) =="The input parameter -x is not supported!"

@patch("docker.from_env")
def test_run_StopIteration(mock_from_env):
    # Test setup
    test_container_arguments = [
        "--name"
    ]
    mock_docker_client = MagicMock()
    mock_from_env.return_value = mock_docker_client

    test_container_engine = container_engine.ContainerEngine()

    with pytest.raises(container_engine.ContainerEngineError) as exported_exception_info:
        # Run unit under test
        test_container_engine.run(test_container_arguments)

        # Check expectations
        assert str(exported_exception_info) =="Invalid input parameter!"

@patch.object(container_engine.ContainerEngine, "user_output")
@patch("docker.from_env")
def test_remove(mock_from_env: MagicMock, mock_user_output: MagicMock) -> None:
    # Test setup
    mock_docker_client = MagicMock()
    mock_from_env.return_value = mock_docker_client

    test_image_to_remove = "test_image_to_remove:latest"

    test_container_engine = container_engine.ContainerEngine()

    # Run unit under test
    test_container_engine.remove(test_image_to_remove)

    # Check expectations
    mock_docker_client.images.remove.assert_called_once_with(test_image_to_remove)

@patch.object(container_engine.ContainerEngine, "user_output")
@patch("docker.from_env")
def test_remove_ImageNotFound(mock_from_env: MagicMock, mock_user_output: MagicMock) -> None:
    # Test setup
    mock_docker_client = MagicMock()
    mock_from_env.return_value = mock_docker_client

    test_image_to_remove = "test_image_to_remove:latest"
    mock_docker_client.images.remove.side_effect = container_engine.docker.errors.ImageNotFound("")

    test_container_engine = container_engine.ContainerEngine()

    # Run unit under test
    test_container_engine.remove(test_image_to_remove)

    # Check expectations
    mock_docker_client.images.remove.assert_called_once_with(test_image_to_remove)
    mock_user_output.msg.assert_called_once_with(f"[yellow]The {test_image_to_remove} doesn't exist. Unable to remove it.[/]\n")

@patch("docker.from_env")
def test_remove_APIError(mock_from_env: MagicMock) -> None:
    # Test setup
    mock_docker_client = MagicMock()
    mock_from_env.return_value = mock_docker_client

    test_image_to_remove = "test_image_to_remove:latest"
    mock_docker_client.images.remove.side_effect = container_engine.docker.errors.APIError("")

    test_container_engine = container_engine.ContainerEngine()

    # Run unit under test
    with pytest.raises(container_engine.ContainerEngineError) as exported_exception_info:
        test_container_engine.remove(test_image_to_remove)

        # Check expectations
        assert str(exported_exception_info) == f"The {test_image_to_remove} is used by a container. Unable to remove it.[/]\n"

        mock_docker_client.images.remove.assert_called_once_with(test_image_to_remove)

@patch("docker.from_env")
def test_search(mock_from_env):
    # Test setup
    mock_docker_client = MagicMock()
    mock_from_env.return_value = mock_docker_client
    test_registry = "test_registry"
    test_repositories = [
        {
            "name": "repo1"
        },
        {
            "name": "repo2"
        },
    ]
    mock_docker_client.images.search.return_value = test_repositories

    test_container_engine = container_engine.ContainerEngine()

    # Run unit under test
    actual_registry_image_list = test_container_engine.search(test_registry)

    # Check expectations
    mock_docker_client.images.search.assert_called_once_with(test_registry)

    expected_registry_image_list = ["repo1", "repo2"]
    assert actual_registry_image_list == expected_registry_image_list