"""Unit tests for the registry."""
# tests/core/test_registry.py

# Unit under test:
import dem.core.registry as registry

# Test framework
import pytest
from unittest.mock import patch, MagicMock, call, PropertyMock

import requests
from typing import Generator

class HelperRegistry(registry.Registry):
    """ The registry.Registry is an abstract base class, so it is not possible to directly 
        instantiate. The HelperRegistry class only acts as a helper for testing.
    """
    def _append_repo_with_tag(self, endpoint_response: dict, repo: str) -> None:
        return super()._append_repo_with_tag(endpoint_response, repo)
    
    def _get_tag_endpoint_url(self, repo_name: str) -> str:
        return super()._get_tag_endpoint_url(repo_name)
    
    def _list_repos_in_registry(self) -> Generator:
        return super()._list_repos_in_registry()

@patch.object(registry.Registry, "_append_repo_with_tag")
@patch.object(registry.Registry, "_get_tag_endpoint_url")
@patch("dem.core.registry.requests.get")
def test_Registry__list_tags(mock_requests_get: MagicMock, mock__get_tag_endpoint_url: MagicMock,
                             mock__append_repo_with_tag: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {}

    test_repo = "test_repo"
    mock_response = MagicMock()
    mock_response.status_code = requests.codes.ok
    test_endpoint_response = "test"
    mock_response.json.return_value = test_endpoint_response
    mock_requests_get.return_value = mock_response
    test_tag_endpoint_url = "test_tag_endpoint_url"
    mock__get_tag_endpoint_url.return_value = test_tag_endpoint_url

    test_registry = HelperRegistry(mock_container_engine, test_registry_config)

    # Run unit under test
    test_registry._list_tags(test_repo)

    # Check expectations
    mock__get_tag_endpoint_url.assert_called_once_with(test_repo)
    mock_requests_get.assert_called_once_with(test_tag_endpoint_url, timeout=10)
    mock_response.json.assert_called_once()
    mock__append_repo_with_tag.assert_called_once_with(test_endpoint_response, test_repo)

@patch.object(registry.Core, "user_output")
@patch.object(registry.Registry, "_get_tag_endpoint_url")
@patch("dem.core.registry.requests.get")
def test_Registry__list_tags_MissingSchema(mock_requests_get: MagicMock, 
                                           mock__get_tag_endpoint_url: MagicMock,
                                           mock_user_output: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {}

    test_repo = "test_repo"
    test_exception_text = "test_exception_text"
    mock_requests_get.side_effect = registry.requests.exceptions.MissingSchema(test_exception_text)
    test_tag_endpoint_url = "test_tag_endpoint_url"
    mock__get_tag_endpoint_url.return_value = test_tag_endpoint_url

    test_registry = HelperRegistry(mock_container_engine, test_registry_config)

    # Run unit under test
    test_registry._list_tags(test_repo)

    # Check expectations
    mock__get_tag_endpoint_url.assert_called_once_with(test_repo)
    mock_requests_get.assert_called_once_with(test_tag_endpoint_url, timeout=10)
    mock_user_output.error.assert_called_once_with(test_exception_text)
    mock_user_output.msg.assert_called_once_with("Skipping repository: " + test_repo)

@patch.object(registry.Core, "user_output")
@patch.object(registry.Registry, "_get_tag_endpoint_url")
@patch("dem.core.registry.requests.get")
def test_Registry__list_tags_invalid_status(mock_requests_get: MagicMock, 
                                            mock__get_tag_endpoint_url: MagicMock,
                                            mock_user_output: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {}

    test_repo = "test_repo"
    mock_response = MagicMock()
    mock_response.status_code = 0
    mock_requests_get.return_value = mock_response
    test_tag_endpoint_url = "test_tag_endpoint_url"
    mock__get_tag_endpoint_url.return_value = test_tag_endpoint_url

    test_registry = HelperRegistry(mock_container_engine, test_registry_config)

    # Run unit under test
    test_registry._list_tags(test_repo)

    # Check expectations
    mock__get_tag_endpoint_url.assert_called_once_with(test_repo)
    mock_requests_get.assert_called_once_with(test_tag_endpoint_url, timeout=10)
    mock_user_output.error.assert_called_once_with("Error in communication with the registry. Failed to retrieve tags. Response status code: " + str(mock_response.status_code))
    mock_user_output.msg.assert_called_once_with("Skipping repository: " + test_repo)

@patch.object(registry.Core, "user_output")
@patch.object(registry.Registry, "_list_repos_in_registry")
def test_Registry_repos(mock__list_repos_in_registry: MagicMock, mock_user_output: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {}

    mock__repos = MagicMock()

    mock_generator = MagicMock()
    mock__list_repos_in_registry.return_value = mock_generator

    test_registry = HelperRegistry(mock_container_engine, test_registry_config)
    test_registry._repos = mock__repos

    # Run unit under test
    actual_repos = test_registry.repos

    # Check expectations
    assert actual_repos is mock__repos

    mock__list_repos_in_registry.assert_called_once()
    mock_user_output.status_generator.assert_called_once_with(mock_generator)

def test_DockerHub__append_repo_with_tag():
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {}

    test_endpoint_response = {
        "results": [
            {
                "name": "latest"
            },
            {
                "name": "v0.0.1"
            }
        ]
    }
    test_repo = "test_repo"

    test_docker_hub = registry.DockerHub(mock_container_engine, test_registry_config)

    # Run unit under test
    test_docker_hub._append_repo_with_tag(test_endpoint_response, test_repo)

    # Check expectations
    expected_repos = []
    for test_result in test_endpoint_response["results"]:
        expected_repos.append(test_repo + ":" + test_result["name"])
    assert expected_repos == test_docker_hub._repos

def test_DockerHub__get_tag_endpoint_url():
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {
        "url": "test_url",
    }

    test_repo = "registry/test_repo"

    test_docker_hub = registry.DockerHub(mock_container_engine, test_registry_config)

    # Run unit under test
    actual_endpoint_url = test_docker_hub._get_tag_endpoint_url(test_repo)

    # Check expectations
    expected_endpoint_url = test_registry_config["url"] + "/v2/repositories/" + test_repo + "/tags/"
    assert expected_endpoint_url == actual_endpoint_url

@patch.object(registry.DockerHub, "_list_tags")
def test_DockerHub__list_repos_in_registry(mock__list_tags: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {
        "name": "test_registry_name"
    }
    test_repos = [
        test_registry_config["name"] + "/test_repo1",
        test_registry_config["name"] + "/test_repo2",
    ]

    mock_container_engine.search.return_value = test_repos

    test_docker_hub = registry.DockerHub(mock_container_engine, test_registry_config)

    # Run unit under test
    generator = test_docker_hub._list_repos_in_registry()

    # Check expectations
    calls = []
    for idx, item in enumerate(generator):
        expected_item = "Loading image data from: " + test_repos[idx]
        assert expected_item == item

        calls.append(call(test_repos[idx]))

    mock_container_engine.search.assert_called_once_with(test_registry_config["name"])
    mock__list_tags.assert_has_calls(calls)

def test_DockerRegistry__append_repo_with_tag():
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {}

    test_endpoint_response = {
        "tags": ["latest", "v0.0.1"]
    }
    test_repo = "test_repo"

    test_docker_registry = registry.DockerRegistry(mock_container_engine, test_registry_config)

    # Run unit under test
    test_docker_registry._append_repo_with_tag(test_endpoint_response, test_repo)

    # Check expectations
    expected_repos = [test_repo + ":" + test_result for test_result in test_endpoint_response["tags"]]
    assert expected_repos == test_docker_registry._repos

def test_DockerRegistry__get_tag_endpoint_url():
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {
        "url": "test_url",
    }

    test_repo = "registry/test_repo"

    test_docker_registry = registry.DockerRegistry(mock_container_engine, test_registry_config)

    # Run unit under test
    actual_endpoint_url = test_docker_registry._get_tag_endpoint_url(test_repo)

    # Check expectations
    expected_endpoint_url = test_registry_config["url"] + "/v2/" + test_repo.split("/")[1] + "/tags/list"
    assert expected_endpoint_url == actual_endpoint_url

@patch.object(registry.DockerRegistry, "_list_tags")
@patch.object(registry.DockerRegistry, "_search")
def test_DockerRegistry__list_repos_in_registry(mock__search: MagicMock, mock__list_tags: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {
        "name": "test_registry_name"
    }
    test_repo_names = [
        "test_repo1",
        "test_repo2",
    ]

    mock__search.return_value = test_repo_names

    test_docker_registry = registry.DockerRegistry(mock_container_engine, test_registry_config)

    # Run unit under test
    generator = test_docker_registry._list_repos_in_registry()

    # Check expectations
    calls = []
    for idx, item in enumerate(generator):
        expected_repo = test_registry_config["name"] + "/" + test_repo_names[idx]
        expected_item = "Loading image data from: " + expected_repo
        assert expected_item == item

        calls.append(call(expected_repo))

    mock__search.assert_called_once()
    mock__list_tags.assert_has_calls(calls)

@patch("dem.core.registry.requests.get")
def test_DockerRegistry__search(mock_requests_get: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {
        "url": "test_url"
    }
    test_response = {
        "repositories": [
            "test_repo1",
            "test_repo2",
        ] 
    }

    mock_response = MagicMock()
    mock_response.status_code = registry.requests.codes.ok
    mock_response.json.return_value = test_response
    mock_requests_get.return_value = mock_response

    test_docker_registry = registry.DockerRegistry(mock_container_engine, test_registry_config)

    # Run unit under test
    actual_repo_names = test_docker_registry._search()

    # Check expectations
    assert actual_repo_names is test_response["repositories"]

    mock_requests_get.assert_called_once_with(test_registry_config["url"] + "/v2/_catalog", timeout=10)
    mock_response.json.assert_called_once()

@patch.object(registry.DockerRegistry, "user_output")
@patch("dem.core.registry.requests.get")
def test_DockerRegistry__search_requests_get_exception(mock_requests_get: MagicMock, mock_user_output: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {
        "name": "test_name",
        "url": "test_url"
    }

    mock_requests_get.side_effect = Exception("test")

    test_docker_registry = registry.DockerRegistry(mock_container_engine, test_registry_config)

    # Run unit under test
    actual_repo_names = test_docker_registry._search()

    # Check expectations
    assert actual_repo_names == []

    mock_requests_get.assert_called_once_with(test_registry_config["url"] + "/v2/_catalog", timeout=10)
    mock_user_output.error(str(mock_requests_get.side_effect))
    mock_user_output.msg("Skipping registry: " + test_registry_config["name"])

@patch.object(registry.DockerRegistry, "user_output")
@patch("dem.core.registry.requests.get")
def test_DockerRegistry__search_invalid_status_code(mock_requests_get: MagicMock, mock_user_output: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {
        "name": "test_name",
        "url": "test_url"
    }

    mock_response = MagicMock()
    mock_response.status_code = 0
    mock_requests_get.return_value = mock_response

    test_docker_registry = registry.DockerRegistry(mock_container_engine, test_registry_config)

    # Run unit under test
    actual_repo_names = test_docker_registry._search()

    # Check expectations
    assert actual_repo_names == []

    mock_requests_get.assert_called_once_with(test_registry_config["url"] + "/v2/_catalog", timeout=10)
    mock_user_output.error("Error in communication with the registry. Failed to retrieve the repositories. Response status code: " + str(mock_response.status_code))
    mock_user_output.msg("Skipping registry: " + test_registry_config["name"])

@patch.object(registry.DockerRegistry, "user_output")
@patch("dem.core.registry.requests.get")
def test_DockerRegistry__search_json_decode_exception(mock_requests_get: MagicMock, 
                                                      mock_user_output: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {
        "name": "test_name",
        "url": "test_url"
    }

    mock_response = MagicMock()
    mock_response.status_code = requests.codes.ok
    mock_response.json.side_effect = requests.exceptions.JSONDecodeError("dummy_msg", "dummy_doc", 0)
    mock_requests_get.return_value = mock_response

    test_docker_registry = registry.DockerRegistry(mock_container_engine, test_registry_config)

    # Run unit under test
    actual_repo_names = test_docker_registry._search()

    # Check expectations
    assert actual_repo_names == []

    mock_requests_get.assert_called_once_with(test_registry_config["url"] + "/v2/_catalog", timeout=10)
    mock_response.json.assert_called_once()
    mock_user_output.error("Invalid JSON format in response. " + str(mock_response.json.side_effect))
    mock_user_output.msg("Skipping registry: " + test_registry_config["name"])

@patch.object(registry.DockerRegistry, "user_output")
@patch("dem.core.registry.requests.get")
def test_DockerRegistry__search_json_generic_exception(mock_requests_get: MagicMock, 
                                                       mock_user_output: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    test_registry_config = {
        "name": "test_name",
        "url": "test_url"
    }

    mock_response = MagicMock()
    mock_response.status_code = requests.codes.ok
    mock_response.json.side_effect = Exception("test")
    mock_requests_get.return_value = mock_response

    test_docker_registry = registry.DockerRegistry(mock_container_engine, test_registry_config)
    
    # Run unit under test
    actual_repo_names = test_docker_registry._search()

    # Check expectations
    assert actual_repo_names == []

    mock_requests_get.assert_called_once_with(test_registry_config["url"] + "/v2/_catalog", timeout=10)
    mock_response.json.assert_called_once()
    mock_user_output.error(str(mock_response.json.side_effect))
    mock_user_output.msg("Skipping registry: " + test_registry_config["name"])

@patch("dem.core.registry.DockerRegistry")
@patch("dem.core.registry.DockerHub")
def test_Registries(mock_DockerHub: MagicMock, mock_DockerRegistry: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    mock_config_file = MagicMock()
    mock_config_file.registries = [
        {
            "name": "registry_config1",
            "url": "registry.hub.docker.com"
        },
        {
            "name": "registry_config2",
            "url": "https://registry_url2.io"
        }
    ]

    mock_docker_hub = MagicMock()
    mock_docker_registry = MagicMock()
    mock_DockerHub.return_value = mock_docker_hub
    mock_DockerHub._docker_hub_domain = "registry.hub.docker.com"
    mock_DockerRegistry.return_value = mock_docker_registry

    # Run unit under test
    test_registries = registry.Registries(mock_container_engine, mock_config_file)

    # Check expectations
    assert test_registries._config_file is mock_config_file
    assert test_registries._container_engine is mock_container_engine
    assert mock_docker_hub in test_registries.registries
    assert mock_docker_registry in test_registries.registries

    mock_DockerHub.assert_called_once_with(mock_container_engine, mock_config_file.registries[0])
    mock_DockerRegistry.assert_called_once_with(mock_container_engine, mock_config_file.registries[1])

@patch("dem.core.registry.DockerRegistry")
@patch("dem.core.registry.DockerHub")
def test_Registries_list_repos(mock_DockerHub: MagicMock, mock_DockerRegistry: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    mock_config_file = MagicMock()
    mock_config_file.registries = [
        {
            "name": "registry_config1",
            "url": "registry.hub.docker.com"
        },
        {
            "name": "registry_config2",
            "url": "https://registry_url2.io"
        }
    ]

    test_repos = [
        "test_repo1",
        "test_repo2",
    ]

    mock_docker_hub = MagicMock()
    mock_docker_hub.repos = test_repos
    mock_docker_registry = MagicMock()
    mock_docker_registry.repos = test_repos
    mock_DockerHub.return_value = mock_docker_hub
    mock_DockerHub._docker_hub_domain = "registry.hub.docker.com"
    mock_DockerRegistry.return_value = mock_docker_registry

    test_registries = registry.Registries(mock_container_engine, mock_config_file)

    # Run unit under test
    actual_repos = test_registries.list_repos()

    # Check expectations
    expected_repos = [*test_repos * 2]
    assert expected_repos == actual_repos

@patch.object(registry.Registries, "user_output")
@patch.object(registry.Registries, "__init__")
def test_Registries_list_repos_handle_exception(mock___init__: MagicMock, 
                                                mock_user_output: MagicMock):
    # Test setup
    mock___init__.return_value = None

    test_exception_text = "test_exception_test"
    test_registry_name = "test_registry_name"
    class StubRegistry():
        def __init__(self) -> None:
            self._registry_config = {
                "name": test_registry_name
            }

        @property
        def repos(self) -> list[str]:
            raise(Exception(test_exception_text))

    test_registries = registry.Registries(MagicMock(), MagicMock())
    test_registries.registries = [StubRegistry()]

    # Run unit under test
    test_registries.list_repos()

    # Check expectations
    mock___init__.assert_called_once()

    calls = [
        call(test_exception_text),
        call("[red]Error: The " + test_registry_name + " registry is not available.[/]")
    ]
    mock_user_output.error.assert_has_calls(calls)

@patch.object(registry.Registries, "_add_registry_instance")
def test_Registries_add_registry(mock__add_registry_instance: MagicMock):
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

    mock__add_registry_instance.assert_called_once_with(registry_to_add)
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
    actual_registry_list = test_registries.list_registry_configs()

    # Check expectations
    assert actual_registry_list is mock_config_file.registries

def test_delete_registry():
    # Test setup
    mock_container_engine = MagicMock()
    mock_config_file = MagicMock()
    mock_config_file.registries = [{
        "name": "test_registry_name",
        "url": "https://registry.hub.docker.com/v2/"
    }]

    test_registries = registry.Registries(mock_container_engine, mock_config_file)

    # Run unit under test
    test_registries.delete_registry(mock_config_file.registries[0])

    # Check expectations
    assert not mock_config_file.registries
    assert not test_registries.registries

    mock_config_file.flush.assert_called_once()