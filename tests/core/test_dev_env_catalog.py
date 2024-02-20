"""Unit tests for the Development Environment Catalog."""
# tests/core/test_dev_env_catalog.py

# Unit under test:
import dem.core.dev_env_catalog as dev_env_catalog

# Test framework
from unittest.mock import patch, MagicMock, call
import pytest

@patch.object(dev_env_catalog.Core, "config_file")
@patch("dem.core.dev_env_catalog.DevEnv")
@patch("dem.core.dev_env_catalog.requests")
def test_DevEnvCatalog_request_dev_envs(mock_requests: MagicMock, mock_DevEnv: MagicMock, 
                       mock_config_file: MagicMock) -> None:
    # Test setup
    mock_response = MagicMock()
    mock_response.status_code = dev_env_catalog.requests.codes.ok

    mock_requests.get.return_value = mock_response
    test_dev_env_descriptors = [MagicMock()] * 5
    mock_json = {
        "development_environments": test_dev_env_descriptors
    }
    mock_response.json.return_value = mock_json

    test_dev_envs = [MagicMock()] * 5
    mock_DevEnv.side_effect = test_dev_envs
    
    test_url = "test_url"
    test_catalog_config = {
        "url": test_url,
        "name": "test_name"
    }

    test_http_request_timeout_s = 1
    mock_config_file.http_request_timeout_s = test_http_request_timeout_s

    test_dev_env_catalog = dev_env_catalog.DevEnvCatalog(test_catalog_config)

    # Run unit under test
    test_dev_env_catalog.request_dev_envs()

    # Check expectations
    assert test_dev_env_catalog.dev_envs == test_dev_envs

    mock_requests.get.assert_called_once_with(test_url, timeout=test_http_request_timeout_s)
    mock_response.json.assert_called_once()

    calls = [call(descriptor=test_dev_env_descriptor) for test_dev_env_descriptor in test_dev_env_descriptors]
    mock_DevEnv.assert_has_calls(calls)

@patch.object(dev_env_catalog.Core, "config_file")
@patch("dem.core.dev_env_catalog.requests")
def test_DevEnvCatalog_request_dev_envs_exception_from_get(mock_requests: MagicMock, 
                                                           mock_config_file: MagicMock) -> None:
    # Test setup
    test_exception_text = "test_exception_text"
    mock_requests.get.side_effect = Exception(test_exception_text)

    test_catalog_config = {
        "url": "test_url",
        "name": "test_name"
    }

    test_http_request_timeout_s = 1
    mock_config_file.http_request_timeout_s = test_http_request_timeout_s

    test_dev_env_catalog = dev_env_catalog.DevEnvCatalog(test_catalog_config)

    # Run unit under test
    with pytest.raises(dev_env_catalog.CatalogError) as e:
        test_dev_env_catalog.request_dev_envs()

    # Check expectations
    assert str(e.value) == f"Catalog error: Error in communication with the [bold]{test_catalog_config['name']}[/bold] Development Environment Catalog.\n{test_exception_text}"

    mock_requests.get.assert_called_once_with(test_catalog_config["url"], 
                                              timeout=test_http_request_timeout_s)

@patch.object(dev_env_catalog.Core, "config_file")
@patch("dem.core.dev_env_catalog.requests")
def test_DevEnvCatalog_request_dev_envs_status_code_not_ok(mock_requests: MagicMock, 
                                                           mock_config_file: MagicMock) -> None:
    # Test setup
    mock_deser_json_response = MagicMock()
    mock_deser_json_response.status_code = dev_env_catalog.requests.codes.not_found
    mock_requests.get.return_value = mock_deser_json_response

    test_catalog_config = {
        "url": "test_url",
        "name": "test_name"
    }

    test_http_request_timeout_s = 1
    mock_config_file.http_request_timeout_s = test_http_request_timeout_s

    test_dev_env_catalog = dev_env_catalog.DevEnvCatalog(test_catalog_config)

    # Run unit under test
    with pytest.raises(dev_env_catalog.CatalogError) as e:
        test_dev_env_catalog.request_dev_envs()

    # Check expectations
    assert str(e.value) == (f"Catalog error: Error in communication with the [bold]{test_catalog_config['name']}[/bold] Development Environment Catalog. " + 
                                  "Failed to retrieve Development Environments." + 
                                  "\nResponse status code: " + str(mock_deser_json_response.status_code) + 
                                  "\nDoes the URL point to a valid Development Environment Catalog?\n")

    mock_requests.get.assert_called_once_with(test_catalog_config["url"], 
                                              timeout=test_http_request_timeout_s)

@patch.object(dev_env_catalog.Core, "config_file")
@patch("dem.core.dev_env_catalog.DevEnv")
@patch("dem.core.dev_env_catalog.requests")
def test_DevEnvCatalog_request_dev_envs_corrupted_dev_env(mock_requests: MagicMock, 
                                                          mock_DevEnv: MagicMock, 
                                                          mock_config_file: MagicMock) -> None:
    # Test setup
    mock_deser_json_response = MagicMock()
    mock_deser_json_response.status_code = dev_env_catalog.requests.codes.ok
    mock_requests.get.return_value = mock_deser_json_response

    mock_dev_env_descriptor = MagicMock()
    mock_deser_json_response.json.return_value = {
        "development_environments": [mock_dev_env_descriptor]
    }

    test_exception_text = "test_exception_text"
    mock_DevEnv.side_effect = Exception(test_exception_text)

    test_catalog_config = {
        "url": "test_url",
        "name": "test_name"
    }

    test_http_request_timeout_s = 1
    mock_config_file.http_request_timeout_s = test_http_request_timeout_s

    test_dev_env_catalog = dev_env_catalog.DevEnvCatalog(test_catalog_config)

    # Run unit under test
    with pytest.raises(dev_env_catalog.CatalogError) as e:
        test_dev_env_catalog.request_dev_envs()

    # Check expectations
    assert str(e.value) == (f"Catalog error: The {test_catalog_config['name']} Development Environment Catalog is corrupted.\n{test_exception_text}")

    mock_requests.get.assert_called_once_with(test_catalog_config["url"], 
                                              timeout=test_http_request_timeout_s)
    mock_deser_json_response.json.assert_called_once()
    mock_DevEnv.assert_called_once_with(descriptor=mock_dev_env_descriptor)

@patch.object(dev_env_catalog.DevEnvCatalog, "__init__")
def test_DevEnvCatalog_get_dev_env_by_name(mock___init__: MagicMock):
    # Test setup
    expected_dev_env_index = 2
    test_dev_env_name = "test_dev_env_name"
    test_dev_envs = [MagicMock()] * 4
    test_dev_envs[expected_dev_env_index].name = test_dev_env_name

    mock___init__.return_value = None

    test_dev_env_catalog = dev_env_catalog.DevEnvCatalog({})
    test_dev_env_catalog.dev_envs = test_dev_envs

    # Run unit under test
    actual_dev_env = test_dev_env_catalog.get_dev_env_by_name(test_dev_env_name)

    # Check expectations
    assert actual_dev_env is test_dev_envs[expected_dev_env_index]
    mock___init__.assert_called_once()

@patch.object(dev_env_catalog.Core, "config_file")
@patch("dem.core.dev_env_catalog.DevEnvCatalog")
def test_DevEnvCatalogs(mock_DevEnvCatalog: MagicMock, mock_config_file: MagicMock) -> None:
    # Test setup
    mock_config_file.catalogs = [
        {
            "url": "test_url_1"
        },
        {
            "url": "test_url_2"
        }
    ]
    mock_dev_env_catalogs = [MagicMock()] * len(mock_config_file.catalogs)
    mock_DevEnvCatalog.side_effect = mock_dev_env_catalogs

    # Run unit under test
    test_dev_env_catalogs = dev_env_catalog.DevEnvCatalogs()

    # Check expectations
    assert test_dev_env_catalogs.catalogs == mock_dev_env_catalogs

    calls = []
    for test_catalog in mock_config_file.catalogs:
        calls.append(call(test_catalog))
    mock_DevEnvCatalog.assert_has_calls(calls)

@patch.object(dev_env_catalog.DevEnvCatalogs, "__init__")
@patch("dem.core.dev_env_catalog.DevEnvCatalog")
def test_DevEnvCatalogs_add_catalog(mock_DevEnvCatalog: MagicMock, mock___init__: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_name = "test_name"
    test_url = "test_url"
    expected_catalog_to_be_added = MagicMock()
    mock_DevEnvCatalog.return_value = expected_catalog_to_be_added

    test_dev_env_catalogs = dev_env_catalog.DevEnvCatalogs()
    test_dev_env_catalogs.catalogs = []
    mock_config_file = MagicMock()
    test_dev_env_catalogs.config_file = mock_config_file
    mock_config_file.catalogs = []

    # Run unit under test
    test_dev_env_catalogs.add_catalog(test_name, test_url)

    # Check expectations
    assert expected_catalog_to_be_added in test_dev_env_catalogs.catalogs 
    assert test_dev_env_catalogs.config_file.catalogs == [{"name": test_name, "url": test_url}]

    mock___init__.assert_called_once()

    mock_DevEnvCatalog.assert_called_once_with({
        "name": test_name,
        "url": test_url
    })
    expected_catalog_to_be_added.request_dev_envs.assert_called_once()
    mock_config_file.flush.assert_called_once()

@patch.object(dev_env_catalog.DevEnvCatalogs, "__init__")
def test_DevEnvCatalogs_add_catalog_exception(mock___init__: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_name = "test_name"
    test_url = "test_url"

    test_dev_env_catalogs = dev_env_catalog.DevEnvCatalogs()
    mock_catalog_with_same_name = MagicMock()
    mock_catalog_with_same_name.name = test_name
    test_dev_env_catalogs.catalogs = [mock_catalog_with_same_name]

    # Run unit under test
    with pytest.raises(dev_env_catalog.CatalogError) as e:
        test_dev_env_catalogs.add_catalog(test_name, test_url)

    # Check expectations
    assert str(e.value) == f"Catalog error: The {test_name} Development Environment Catalog name is already used."

    mock___init__.assert_called_once()

@patch.object(dev_env_catalog.Core, "config_file")
@patch("dem.core.dev_env_catalog.DevEnvCatalog")
def test_DevEnvCatalogs_delete_catalog(mock_DevEnvCatalog: MagicMock, 
                                       mock_config_file: MagicMock) -> None:
    # Test setup
    catalog_config_to_delete = {
        "name": "test_catalog_to_delete",
        "url": "test_url"
    }
    another_catalog_config = {
        "name": "test_another_catalog",
        "url": "test_url"
    }

    mock_catalog_to_delete = MagicMock()
    mock_catalog_to_delete.name = catalog_config_to_delete["name"]
    mock_catalog_to_delete.config = catalog_config_to_delete
    mock_another_catalog = MagicMock()
    mock_another_catalog.name = another_catalog_config["name"]
    mock_DevEnvCatalog.side_effect = [mock_catalog_to_delete, mock_another_catalog]

    dev_env_catalog.Core.config_file.catalogs = [catalog_config_to_delete, another_catalog_config]
    test_dev_env_catalogs = dev_env_catalog.DevEnvCatalogs()

    # Run unit under test
    test_dev_env_catalogs.delete_catalog(catalog_config_to_delete["name"])

    # Check expectations
    assert mock_catalog_to_delete not in test_dev_env_catalogs.catalogs
    assert catalog_config_to_delete not in test_dev_env_catalogs.config_file.catalogs

    mock_config_file.flush.assert_called_once()

@patch.object(dev_env_catalog.DevEnvCatalogs, "__init__")
@patch("dem.core.dev_env_catalog.DevEnvCatalog")
def test_DevEnvCatalogs_delete_catalog_not_existing(mock_DevEnvCatalog: MagicMock, 
                                                    mock___init__) -> None:
    # Test setup
    mock___init__.return_value = None

    mock_catalog_to_delete = MagicMock()
    mock_catalog_to_delete.name = "test_catalog_to_delete"
    mock_another_catalog = MagicMock()
    mock_another_catalog.name = "test_another_catalog"

    test_dev_env_catalogs = dev_env_catalog.DevEnvCatalogs()
    test_dev_env_catalogs.catalogs = [mock_another_catalog, mock_catalog_to_delete]

    # Run unit under test
    with pytest.raises(dev_env_catalog.CatalogError) as e:
        test_dev_env_catalogs.delete_catalog("not_existing_name")

    # Check expectations
    assert str(e.value) == "Catalog error: The not_existing_name Development Environment Catalog doesn't exist."

    mock___init__.assert_called_once()