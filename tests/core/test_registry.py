"""Unit tests for the registry."""
# tests/core/test_registry.py

# Unit under test:
import dem.core.registry as registry

# Test framework
import pytest
from unittest.mock import patch, MagicMock, call

import requests
from dem.core.exceptions import RegistryError
from typing import Generator

def fake_response(status_code: int, json_data: str) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.json = lambda: json_data
    return response

@patch("dem.core.registry.requests.get")
def test__list_repos_in_registry(mock_requests_get):
    # Test setup
    mock_container_engine = MagicMock()
    mock_config_file = MagicMock()
    test_image_names = [
        "test_image_1",
        "test_image_2",
        "test_image_3",
    ]
    mock_container_engine.search.return_value = test_image_names
    test_json_results = [
        {
            "results": [
                {
                    "name": "latest"
                },
                {
                    "name": "v0.0.1"
                }
            ]
        },
        {
            "results": [
                {
                    "name": "latest"
                }
            ]
        },
        {
            "results": [
                {
                    "name": "latest"
                }
            ]
        }
    ]
    fake_responses = [
        fake_response(requests.codes.ok, test_json_results[0]),
        fake_response(requests.codes.ok, test_json_results[1]),
        fake_response(requests.codes.ok, test_json_results[2]),
    ]
    mock_requests_get.side_effect = fake_responses

    test_registries = registry.Registries(mock_container_engine, mock_config_file)

    test_registry = {
        "name": "test_registry_name",
        "url": "https://registry.hub.docker.com/v2/"
    }
    actual_repo_list = []

    # Run unit under test
    actual_generator = test_registries._list_repos_in_registry(test_registry, actual_repo_list)

    # Check expectations
    assert test_registries._container_engine is mock_container_engine
    assert test_registries._config_file is mock_config_file

    for item, test_image_name in zip(actual_generator, test_image_names):
        assert item == "Loading image data from " + test_registry["name"] + ": " + test_image_name

    mock_container_engine.search.assert_called_once_with(test_registry["name"])
    calls = []
    for test_image_name in test_image_names:
        calls.append(call(test_registry["url"] + "repositories/" + test_image_name + "/tags/"))
    mock_requests_get.assert_has_calls(calls)
    
    expected_images = [
        "test_image_1:latest",
        "test_image_1:v0.0.1",
        "test_image_2:latest",
        "test_image_3:latest",
    ]
    assert expected_images == actual_repo_list

@patch("dem.core.registry.requests.get")
def test__list_repos_in_registry_registry_error(mock_requests_get):
    # Test setup
    mock_container_engine = MagicMock()
    mock_config_file = MagicMock()
    test_image_names = [
        "test_image_1",
    ]
    mock_container_engine.search.return_value = test_image_names
    fake_response = MagicMock()
    fake_response.status_code = 500
    mock_requests_get.return_value = fake_response

    test_registry = {
        "name": "test_registry_name",
        "url": "https://registry.hub.docker.com/v2/"
    }
    actual_repo_list = []

    test_registries = registry.Registries(mock_container_engine, mock_config_file)

    # Run unit under test
    with pytest.raises(RegistryError) as exported_exception_info:
        actual_generator =  test_registries._list_repos_in_registry(test_registry, actual_repo_list)

        # Check expectations
        for item, test_image_name in zip(actual_generator, test_image_names):
            assert item == "Loading image data from " + test_registry["name"] + ": " + test_image_name

        mock_container_engine.search.assert_called_once_with(test_registry["name"])
        mock_requests_get.assert_called_once_with(test_registry["url"] + "repositories/" + test_image_names[0] + "/tags/")

        assert str(exported_exception_info.value) == "Error in communication with the registry. Failed to retrieve tags. Response status code: 500"
        assert actual_repo_list == []

@patch.object(registry.Core, "user_output")
@patch("dem.core.registry.requests.get")
def test__list_repos_in_registry_MissingSchema(mock_requests_get: MagicMock, 
                                               mock_user_output: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    mock_config_file = MagicMock()
    test_image_names = [
        "test_image_1",
    ]
    mock_container_engine.search.return_value = test_image_names
    mock_requests_get.side_effect = requests.exceptions.MissingSchema("dummy")

    test_registry = {
        "name": "test_registry_name",
        "url": "https://registry.hub.docker.com/v2/"
    }
    actual_repo_list = []

    test_registries = registry.Registries(mock_container_engine, mock_config_file)

    # Run unit under test
    actual_generator =  test_registries._list_repos_in_registry(test_registry, actual_repo_list)

    # Check expectations
    for item, test_image_name in zip(actual_generator, test_image_names):
        assert item == "Loading image data from " + test_registry["name"] + ": " + test_image_name

    mock_container_engine.search.assert_called_once_with(test_registry["name"])
    mock_requests_get.assert_called_once_with(test_registry["url"] + "repositories/" + test_image_names[0] + "/tags/")
    mock_user_output.error.assert_called_once_with(str(mock_requests_get.side_effect))
    mock_user_output.msg.assert_called_once_with("Skipping this repository.")

    assert actual_repo_list == []

@patch.object(registry.Core, "user_output")
def test_list_repos(mock_user_output: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    mock_config_file = MagicMock()

    mock_config_file.registries = [
        {
            "name": "test_registry_name",
            "url": "https://registry.hub.docker.com/v2/"
        },
        {
            "name": "test_registry_name2",
            "url": "https://registry.hub.docker.com/v2/22"
        }
    ]

    mock_list_repos_in_registry_generator = MagicMock()
    expected_list_of_repos = [
        "test_repo1",
        "test_repo2"
    ]
    call_cntr: int = 0
    def stub__list_repos_in_registry(self, registry: dict, repo_list: list[str]) -> Generator:
        nonlocal call_cntr

        assert registry in mock_config_file.registries
        repo_list.append(expected_list_of_repos[call_cntr])
        call_cntr += 1
        return mock_list_repos_in_registry_generator
    registry.Registries._list_repos_in_registry = stub__list_repos_in_registry

    test_registries = registry.Registries(mock_container_engine, mock_config_file)

    # Run unit under test
    actual_list_of_repos = test_registries.list_repos()

    # Check expectations
    assert actual_list_of_repos == expected_list_of_repos
    mock_user_output.status_generator.assert_called_with(mock_list_repos_in_registry_generator)

def test_add_registry():
    # Test setup
    mock_container_engine = MagicMock()
    mock_config_file = MagicMock()
    mock_config_file.registries = []

    registry_to_add = {
        "name": "test_registry_name",
        "url": "https://registry.hub.docker.com/v2/"
    }

    test_registries = registry.Registries(mock_container_engine, mock_config_file)

    # Run unit under test
    test_registries.add_registry(registry_to_add)

    # Check expectations
    assert registry_to_add in mock_config_file.registries

    mock_config_file.flush.assert_called_once()

def test_list_registries():
    # Test setup
    mock_container_engine = MagicMock()
    mock_config_file = MagicMock()
    mock_config_file.registries = [{
        "name": "test_registry_name",
        "url": "https://registry.hub.docker.com/v2/"
    }]

    test_registries = registry.Registries(mock_container_engine, mock_config_file)

    # Run unit under test
    actual_registry_list = test_registries.list_registries()

    # Check expectations
    assert actual_registry_list is mock_config_file.registries