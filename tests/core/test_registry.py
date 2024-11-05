"""Unit tests for the registry."""
# tests/core/test_registry.py

# Unit under test:
import dem.core.registry as registry

# Test framework
import pytest
from unittest.mock import patch, MagicMock, call

import requests

class HelperRegistry(registry.Registry):
    """ The registry.Registry is an abstract base class, so it is not possible to directly 
        instantiate. The HelperRegistry class only acts as a helper for testing.
    """
    _tag_endpoint_response_key = "results"
    _repo_endpoint_response_key = "repositories"

    def _append_repo_with_tag(self, endpoint_response: dict, repo: str) -> None:
        return super()._append_repo_with_tag(endpoint_response, repo)

    def _get_repo_endpoint_url(self) -> str:
        return super()._get_repo_endpoint_url()
    
    def _get_tag_endpoint_url(self, repo_name: str) -> str:
        return super()._get_tag_endpoint_url(repo_name)

def test_Registry___init___RegistryError() -> None:
    # Test setup
    test_registry_config = {}

    # Run unit under test
    with pytest.raises(registry.RegistryError):
        HelperRegistry(test_registry_config)

@patch.object(registry.Core, "config_file")
@patch.object(registry.Registry, "_append_repo_with_tag")
@patch.object(registry.Registry, "_get_tag_endpoint_url")
@patch.object(registry.Registry, "__init__")
@patch("dem.core.registry.requests.get")
def test_Registry__list_tags(mock_requests_get: MagicMock, mock___init__: MagicMock,
                             mock__get_tag_endpoint_url: MagicMock,
                             mock__append_repo_with_tag: MagicMock, mock_config_file: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_registry_config = {}

    test_repo = "test_repo"
    mock_response = MagicMock()
    mock_response.status_code = requests.codes.ok
    test_endpoint_response = "test"
    mock_response.json.return_value = test_endpoint_response
    mock_requests_get.return_value = mock_response
    test_tag_endpoint_url = "test_tag_endpoint_url"
    mock__get_tag_endpoint_url.return_value = test_tag_endpoint_url

    test_http_request_timeout_s = 10
    mock_config_file.http_request_timeout_s = test_http_request_timeout_s

    test_registry = HelperRegistry(test_registry_config)

    # Run unit under test
    test_registry._list_tags(test_repo)

    # Check expectations
    mock___init__.assert_called_once()
    mock__get_tag_endpoint_url.assert_called_once_with(test_repo)
    mock_requests_get.assert_called_once_with(test_tag_endpoint_url, timeout=test_http_request_timeout_s)
    mock_response.json.assert_called_once()
    mock__append_repo_with_tag.assert_called_once_with(test_endpoint_response, test_repo)

@patch.object(registry.Core, "config_file")
@patch.object(registry.Core, "user_output")
@patch.object(registry.Registry, "_get_tag_endpoint_url")
@patch.object(registry.Registry, "__init__")
@patch("dem.core.registry.requests.get")
def test_Registry__list_tags_MissingSchema(mock_requests_get: MagicMock, mock___init__: MagicMock,
                                           mock__get_tag_endpoint_url: MagicMock,
                                           mock_user_output: MagicMock, mock_config_file: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_registry_config = {}

    test_repo = "test_repo"
    test_exception_text = "test_exception_text"
    mock_requests_get.side_effect = registry.requests.exceptions.MissingSchema(test_exception_text)
    test_tag_endpoint_url = "test_tag_endpoint_url"
    mock__get_tag_endpoint_url.return_value = test_tag_endpoint_url

    test_http_request_timeout_s = 10
    mock_config_file.http_request_timeout_s = test_http_request_timeout_s

    test_registry = HelperRegistry(test_registry_config)

    # Run unit under test
    test_registry._list_tags(test_repo)

    # Check expectations
    mock___init__.assert_called_once()
    mock__get_tag_endpoint_url.assert_called_once_with(test_repo)
    mock_requests_get.assert_called_once_with(test_tag_endpoint_url, timeout=test_http_request_timeout_s)
    mock_user_output.error.assert_called_once_with(test_exception_text)
    mock_user_output.msg.assert_called_once_with("Skipping repository: " + test_repo)

@patch.object(registry.Core, "config_file")
@patch.object(registry.Core, "user_output")
@patch.object(registry.Registry, "_get_tag_endpoint_url")
@patch.object(registry.Registry, "__init__")
@patch("dem.core.registry.requests.get")
def test_Registry__list_tags_invalid_status(mock_requests_get: MagicMock, mock___init__: MagicMock,
                                            mock__get_tag_endpoint_url: MagicMock,
                                            mock_user_output: MagicMock, 
                                            mock_config_file: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_registry_config = {}

    test_repo = "test_repo"
    mock_response = MagicMock()
    mock_response.status_code = 0
    mock_requests_get.return_value = mock_response
    test_tag_endpoint_url = "test_tag_endpoint_url"
    mock__get_tag_endpoint_url.return_value = test_tag_endpoint_url

    test_http_request_timeout_s = 10
    mock_config_file.http_request_timeout_s = test_http_request_timeout_s

    test_registry = HelperRegistry(test_registry_config)

    # Run unit under test
    test_registry._list_tags(test_repo)

    # Check expectations
    mock___init__.assert_called_once()
    mock__get_tag_endpoint_url.assert_called_once_with(test_repo)
    mock_requests_get.assert_called_once_with(test_tag_endpoint_url, timeout=test_http_request_timeout_s)
    mock_user_output.error.assert_called_once_with("Error in communication with the registry. Failed to retrieve tags. Response status code: " + str(mock_response.status_code))
    mock_user_output.msg.assert_called_once_with("Skipping repository: " + test_repo)

@patch("dem.core.registry.requests.get")
@patch.object(registry.Registry, "_list_tags")
@patch.object(registry.Registry, "_get_repo_endpoint_url")
@patch.object(registry.Registry, "__init__")
def test_Registry__list_repos(mock___init__: MagicMock, mock__get_repo_endpoint_url: MagicMock,
                              mock__list_tags: MagicMock, mock_requests_get: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_repo_endpoint_url = "test_repo_endpoint_url"
    mock__get_repo_endpoint_url.return_value = test_repo_endpoint_url

    mock_response = MagicMock()
    mock_response.status_code = requests.codes.ok

    test_endpoint_response = {
        "repositories": [
            {
                "name": "test_repo1"
            },
            {
                "name": "test_repo2"
            }
        ]
    }

    mock_requests_get.return_value = mock_response
    mock_response.json.return_value = test_endpoint_response

    test_registry = HelperRegistry({})
    test_registry.config_file.http_request_timeout_s = 10

    # Run unit under test
    actual_generator_items = []
    for item in test_registry._list_repos():
        actual_generator_items.append(item)

    # Check expectations
    expected_generator_items = [
        "Loading image data from: test_repo1",
        "Loading image data from: test_repo2"
    ]
    assert expected_generator_items == actual_generator_items

    mock___init__.assert_called_once()
    mock_requests_get.assert_called_once_with(test_repo_endpoint_url, 
                                               timeout=test_registry.config_file.http_request_timeout_s)
    mock_response.json.assert_called_once()
    mock__list_tags.assert_has_calls([call("test_repo1"), call("test_repo2")])

@patch("dem.core.registry.requests.get")
@patch.object(registry.Registry, "user_output")
@patch.object(registry.Registry, "_get_repo_endpoint_url")
def test_Registry__list_repos_requests_get_Exception(mock__get_repo_endpoint_url: MagicMock,
                                                     mock_user_output: MagicMock, 
                                                     mock_requests_get: MagicMock) -> None:
    # Test setup
    test_registry_config = {
        "url": "test_url",
        "name": "test_name",
        "namespace": "test_namespace"
    }

    test_repo_endpoint_url = "test_repo_endpoint_url"
    mock__get_repo_endpoint_url.return_value = test_repo_endpoint_url

    test_exception_text = "test_exception_text"
    mock_requests_get.side_effect = Exception(test_exception_text)

    test_registry = HelperRegistry(test_registry_config)
    test_registry.config_file.http_request_timeout_s = 10

    # Run unit under test
    for _ in test_registry._list_repos():
        pass

    # Check expectations
    mock_requests_get.assert_called_once_with(test_repo_endpoint_url, 
                                               timeout=test_registry.config_file.http_request_timeout_s)
    mock_user_output.error.assert_called_once_with(test_exception_text)
    mock_user_output.msg.assert_called_once_with(f"Skipping [bold]{test_registry_config['name']}[/bold].")

@patch("dem.core.registry.requests.get")
@patch.object(registry.Registry, "user_output")
@patch.object(registry.Registry, "_get_repo_endpoint_url")
def test_Registry__list_repos_request_failed(mock__get_repo_endpoint_url: MagicMock,
                                             mock_user_output: MagicMock, 
                                             mock_requests_get: MagicMock) -> None:
    # Test setup
    test_registry_config = {
        "url": "test_url",
        "name": "test_name",
        "namespace": "test_namespace"
    }

    test_repo_endpoint_url = "test_repo_endpoint_url"
    mock__get_repo_endpoint_url.return_value = test_repo_endpoint_url

    mock_response = MagicMock()
    mock_response.status_code = "404"

    mock_requests_get.return_value = mock_response

    test_registry = HelperRegistry(test_registry_config)
    test_registry.config_file.http_request_timeout_s = 10

    # Run unit under test
    for _ in test_registry._list_repos():
        pass

    # Check expectations
    mock_requests_get.assert_called_once_with(test_repo_endpoint_url, 
                                               timeout=test_registry.config_file.http_request_timeout_s)
    mock_user_output.error.assert_called_once_with(f"Error in communication with the registry. Failed to retrieve the repositories. Response status code: {mock_response.status_code}")
    mock_user_output.msg.assert_called_once_with(f"Skipping [bold]{test_registry_config['name']}[/bold].")

@patch("dem.core.registry.requests.get")
@patch.object(registry.Registry, "user_output")
@patch.object(registry.Registry, "_get_repo_endpoint_url")
def test_Registry__list_repos_JSONDecodeError(mock__get_repo_endpoint_url: MagicMock,
                                              mock_user_output: MagicMock, 
                                              mock_requests_get: MagicMock) -> None:
    # Test setup
    test_registry_config = {
        "url": "test_url",
        "name": "test_name",
        "namespace": "test_namespace"
    }

    test_repo_endpoint_url = "test_repo_endpoint_url"
    mock__get_repo_endpoint_url.return_value = test_repo_endpoint_url

    mock_response = MagicMock()
    mock_response.status_code = requests.codes.ok

    mock_requests_get.return_value = mock_response
    mock_response.json.side_effect = registry.requests.exceptions.JSONDecodeError("test", "test", 0)

    test_registry = HelperRegistry(test_registry_config)
    test_registry.config_file.http_request_timeout_s = 10

    # Run unit under test
    for _ in test_registry._list_repos():
        pass

    # Check expectations
    mock_requests_get.assert_called_once_with(test_repo_endpoint_url, 
                                               timeout=test_registry.config_file.http_request_timeout_s)
    mock_response.json.assert_called_once()
    mock_user_output.error.assert_called_once_with(f"Invalid JSON format in response from the registry: test: line 1 column 1 (char 0)")
    mock_user_output.msg.assert_called_once_with(f"Skipping [bold]{test_registry_config['name']}[/bold].")

@patch("dem.core.registry.requests.get")
@patch.object(registry.Registry, "user_output")
@patch.object(registry.Registry, "_get_repo_endpoint_url")
def test_Registry__list_repos_json_Exception(mock__get_repo_endpoint_url: MagicMock,
                                             mock_user_output: MagicMock, 
                                             mock_requests_get: MagicMock) -> None:
    # Test setup
    test_registry_config = {
        "url": "test_url",
        "name": "test_name",
        "namespace": "test_namespace"
    }

    test_repo_endpoint_url = "test_repo_endpoint_url"
    mock__get_repo_endpoint_url.return_value = test_repo_endpoint_url

    mock_response = MagicMock()
    mock_response.status_code = requests.codes.ok

    mock_requests_get.return_value = mock_response
    test_exception_text = "test_exception_text"
    mock_response.json.side_effect = Exception(test_exception_text)

    test_registry = HelperRegistry(test_registry_config)
    test_registry.config_file.http_request_timeout_s = 10

    # Run unit under test
    for _ in test_registry._list_repos():
        pass

    # Check expectations
    mock_requests_get.assert_called_once_with(test_repo_endpoint_url, 
                                               timeout=test_registry.config_file.http_request_timeout_s)
    mock_response.json.assert_called_once()
    mock_user_output.error.assert_called_once_with(test_exception_text)
    mock_user_output.msg.assert_called_once_with(f"Skipping [bold]{test_registry_config['name']}[/bold].")

@patch.object(registry.Core, "user_output")
@patch.object(registry.Registry, "_list_repos")
@patch.object(registry.Registry, "__init__")
def test_Registry_repos(mock___init_: MagicMock, mock__list_repos: MagicMock, 
                        mock_user_output: MagicMock):
    # Test setup
    mock___init_.return_value = None

    test_registry_config = {}

    mock__repos = MagicMock()

    mock_generator = MagicMock()
    mock__list_repos.return_value = mock_generator

    test_registry = HelperRegistry(test_registry_config)
    test_registry._repos = mock__repos

    # Run unit under test
    actual_repos = test_registry.repos

    # Check expectations
    assert actual_repos is mock__repos

    mock___init_.assert_called_once()
    mock__list_repos.assert_called_once()
    mock_user_output.status_generator.assert_called_once_with(mock_generator)

def test_DockerHub_invalid_registry_config() -> None:
    # Test setup
    test_registry_config = {
        "url": "test_url",
        "name": "test_name"
    }

    # Run unit under test
    with pytest.raises(registry.RegistryError) as exported_exception_info:
        registry.DockerHub(test_registry_config)

    # Check expectations
    assert "Registry error: Invalid registry configuration. For Docker Hub the namespace must be set." == str(exported_exception_info.value)

@patch.object(registry.DockerHub, "__init__")
def test_DockerHub__append_repo_with_tag(mock___init__: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

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
    test_namespace = "test_namespace"

    test_docker_hub = registry.DockerHub(test_registry_config)
    test_docker_hub._repos = []
    test_docker_hub._namespace = test_namespace

    # Run unit under test
    test_docker_hub._append_repo_with_tag(test_endpoint_response, test_repo)

    # Check expectations
    expected_repos = []
    for test_result in test_endpoint_response["results"]:
        expected_repos.append(test_namespace + "/" + test_repo + ":" + test_result["name"])
    assert expected_repos == test_docker_hub._repos

    mock___init__.assert_called_once()

def test_DockerHub__get_repo_endpoint_url():
    # Test setup
    test_registry_config = {
        "url": "test_url",
        "name": "test_name",
        "namespace": "test_namespace"
    }

    test_docker_hub = registry.DockerHub(test_registry_config)

    # Run unit under test
    actual_endpoint_url = test_docker_hub._get_repo_endpoint_url()

    # Check expectations
    expected_endpoint_url = f"{test_registry_config['url']}/v2/namespaces/{test_registry_config['namespace']}/repositories"
    assert expected_endpoint_url == actual_endpoint_url

def test_DockerHub__get_tag_endpoint_url():
    # Test setup
    test_registry_config = {
        "url": "test_url",
        "name": "test_name",
        "namespace": "test_namespace"
    }

    test_repo = "registry/test_repo"

    test_docker_hub = registry.DockerHub(test_registry_config)

    # Run unit under test
    actual_endpoint_url = test_docker_hub._get_tag_endpoint_url(test_repo)

    # Check expectations
    expected_endpoint_url = f"{test_registry_config['url']}/v2/namespaces/{test_registry_config['namespace']}/repositories/{test_repo}/tags"
    assert expected_endpoint_url == actual_endpoint_url


@patch.object(registry.Registry, "__init__")
def test_DockerRegistry__append_repo_with_tag(mock___init__: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_registry_config = {}

    test_endpoint_response = {
        "tags": ["latest", "v0.0.1"]
    }
    test_repo = "test_repo"
    test_registry_url = "test_registry_url"

    test_docker_registry = registry.DockerRegistry(test_registry_config)
    test_docker_registry._repos = []
    test_docker_registry._url = test_registry_url

    # Run unit under test
    test_docker_registry._append_repo_with_tag(test_endpoint_response, test_repo)

    # Check expectations
    expected_repos = [test_registry_url + "/" + test_repo + ":" + test_result for test_result in test_endpoint_response["tags"]]
    assert expected_repos == test_docker_registry._repos

    mock___init__.assert_called_once()

def test_DockerRegistry__get_repo_endpoint_url():
    # Test setup
    test_registry_config = {
        "url": "test_url",
        "name": "test_name",
        "namespace": "test_namespace"
    }

    test_docker_registry = registry.DockerRegistry(test_registry_config)

    # Run unit under test
    actual_endpoint_url = test_docker_registry._get_repo_endpoint_url()

    # Check expectations
    expected_endpoint_url = f"{test_registry_config['url']}/v2/_catalog"
    assert expected_endpoint_url == actual_endpoint_url

def test_DockerRegistry__get_tag_endpoint_url():
    # Test setup
    test_registry_config = {
        "url": "test_url",
        "name": "test_name",
        "namespace": "test_namespace"
    }

    test_repo = "registry/test_repo"

    test_docker_registry = registry.DockerRegistry(test_registry_config)

    # Run unit under test
    actual_endpoint_url = test_docker_registry._get_tag_endpoint_url(test_repo)

    # Check expectations
    expected_endpoint_url = f"{test_registry_config['url']}/v2/{test_repo.split('/')[1]}/tags/list"
    assert expected_endpoint_url == actual_endpoint_url

@patch.object(registry.Core, "config_file")
@patch("dem.core.registry.DockerRegistry")
@patch("dem.core.registry.DockerHub")
def test_Registries(mock_DockerHub: MagicMock, mock_DockerRegistry: MagicMock, 
                    mock_config_file: MagicMock) -> None:
    # Test setup
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
    test_registries = registry.Registries()

    # Check expectations
    assert mock_docker_hub in test_registries.registries
    assert mock_docker_registry in test_registries.registries

    mock_DockerHub.assert_called_once_with(mock_config_file.registries[0])
    mock_DockerRegistry.assert_called_once_with(mock_config_file.registries[1])

@patch.object(registry.Core, "config_file")
@patch("dem.core.registry.DockerRegistry")
@patch("dem.core.registry.DockerHub")
def test_Registries_list_repos(mock_DockerHub: MagicMock, mock_DockerRegistry: MagicMock,
                               mock_config_file: MagicMock) -> None:
    # Test setup
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

    test_registries = registry.Registries()

    # Run unit under test
    actual_repos = test_registries.list_repos([])

    # Check expectations
    expected_repos = [*test_repos * 2]
    assert expected_repos == actual_repos

@patch.object(registry.Core, "config_file")
@patch.object(registry.Registries, "_add_registry_instance")
def test_Registries_add_registry(mock__add_registry_instance: MagicMock, 
                                 mock_config_file: MagicMock) -> None:
    # Test setup
    mock_config_file.registries = []

    registry_to_add = {
        "name": "test_registry_name",
        "url": "https://registry.hub.docker.com/v2/"
    }

    test_registries = registry.Registries()

    # Run unit under test
    test_registries.add_registry(registry_to_add)

    # Check expectations
    assert registry_to_add in mock_config_file.registries

    mock__add_registry_instance.assert_called_once_with(registry_to_add)
    mock_config_file.flush.assert_called_once()

@patch.object(registry.Core, "config_file")
def test_Registries_list_registry_configs(mock_config_file: MagicMock) -> None:
    # Test setup
    mock_config_file.registries = [{
        "name": "test_registry_name",
        "url": "https://registry.hub.docker.com/v2/",
        "namespace": "test_namespace"
    }]

    test_registries = registry.Registries()

    # Run unit under test
    actual_registry_list = test_registries.list_registry_configs()

    # Check expectations
    assert actual_registry_list is mock_config_file.registries

@patch.object(registry.Core, "config_file")
def test_Registries_delete_registry(mock_config_file: MagicMock) -> None:
    # Test setup
    mock_config_file.registries = [{
        "name": "test_registry_name",
        "url": "https://registry.hub.docker.com/v2/",
        "namespace": "test_namespace"
    }]

    test_registries = registry.Registries()

    # Run unit under test
    test_registries.delete_registry(mock_config_file.registries[0])

    # Check expectations
    assert not mock_config_file.registries
    assert not test_registries.registries

    mock_config_file.flush.assert_called_once()