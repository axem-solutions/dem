"""Unit tests for the registry."""
# tests/core/test_registry.py

# Unit under test:
import dem.core.registry as registry

# Test framework
import pytest
from unittest.mock import patch, MagicMock, call

import requests
from dem.core.exceptions import RegistryError

def fake_response(status_code: int, json_data: str) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.json = lambda: json_data
    return response

@patch("dem.core.registry.requests.get")
def test_list_repos(mock_requests_get):
    # Test setup
    mock_container_engine = MagicMock()
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

    test_registries = registry.Registries(mock_container_engine)

    # Run unit under test
    actual_images = test_registries.list_repos()

    # Check expectations
    mock_container_engine.search.assert_called_once_with("axemsolutions")
    calls = []
    for test_image_name in test_image_names:
        calls.append(call(f"https://registry.hub.docker.com/v2/repositories/{test_image_name}/tags/"))
    mock_requests_get.assert_has_calls(calls)
    
    expected_images = [
        "test_image_1:latest",
        "test_image_1:v0.0.1",
        "test_image_2:latest",
        "test_image_3:latest",
    ]
    assert expected_images == actual_images

@patch("dem.core.registry.requests.get")
def test_list_repos_registry_error(mock_requests_get):
    # Test setup
    mock_container_engine = MagicMock()
    test_image_names = [
        "test_image_1",
    ]
    mock_container_engine.search.return_value = test_image_names
    fake_response = MagicMock()
    fake_response.status_code = 500
    mock_requests_get.return_value = fake_response

    test_registries = registry.Registries(mock_container_engine)

    # Run unit under test
    with pytest.raises(RegistryError) as exported_exception_info:
        test_registries.list_repos()
        assert str(exported_exception_info.value) == "Error in communication with the registry. Failed to retrieve tags. Response status code: 500"