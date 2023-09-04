"""Unit tests for the Development Environment Catalog."""
# tests/core/test_dev_env_catalog.py

# Unit under test:
import dem.core.dev_env_catalog as dev_env_catalog

# Test framework
from unittest.mock import patch, MagicMock, call

@patch("dem.core.dev_env_catalog.DevEnv")
@patch("dem.core.dev_env_catalog.requests")
def test_DevEnvCatalog(mock_requests: MagicMock, mock_DevEnv: MagicMock):
    # Test setup
    mock_response = MagicMock()
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
        "url": test_url
    }

    # Run unit under test
    test_dev_env_catalog = dev_env_catalog.DevEnvCatalog(test_catalog_config)

    # Check expectations
    assert test_dev_env_catalog.dev_envs == test_dev_envs

    mock_requests.get.assert_called_once_with(test_url, timeout=1)
    mock_response.json.assert_called_once()

    calls = [call(descriptor=test_dev_env_descriptor) for test_dev_env_descriptor in test_dev_env_descriptors]
    mock_DevEnv.assert_has_calls(calls)

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

@patch("dem.core.dev_env_catalog.DevEnvCatalog")
def test_DevEnvCatalogs(mock_DevEnvCatalog: MagicMock):
    # Test setup
    mock_config_file = MagicMock()
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
    test_dev_env_catalogs = dev_env_catalog.DevEnvCatalogs(mock_config_file)

    # Check expectations
    assert test_dev_env_catalogs.catalogs == mock_dev_env_catalogs

    calls = []
    for test_catalog in mock_config_file.catalogs:
        calls.append(call(test_catalog))
    mock_DevEnvCatalog.assert_has_calls(calls)

@patch("dem.core.dev_env_catalog.DevEnvCatalog")
def test_DevEnvCatalogs_add_catalog(mock_DevEnvCatalog: MagicMock):
    # Test setup
    mock_config_file = MagicMock()
    test_default_catalogs = [
        {
            "url": "test_url_1"
        },
        {
            "url": "test_url_2"
        }
    ]
    # A copy needed,because the test_default_catalogs list used later for checking the expectations.
    mock_config_file.catalogs = test_default_catalogs.copy()
    mock_dev_env_catalogs = [MagicMock()] * len(mock_config_file.catalogs)
    expected_catalog_config_to_be_added = {
        "url": "test_url"
    }
    expected_catalog_to_be_added = MagicMock()
    # When the DevEnvCatalog gets called from the add_catalog(), it returns with the last item from 
    # the list.
    mock_dev_env_catalogs.append(expected_catalog_to_be_added)
    mock_DevEnvCatalog.side_effect = mock_dev_env_catalogs

    test_dev_env_catalogs = dev_env_catalog.DevEnvCatalogs(mock_config_file)

    # Run unit under test
    test_dev_env_catalogs.add_catalog(expected_catalog_config_to_be_added)

    # Check expectations
    assert expected_catalog_to_be_added in test_dev_env_catalogs.catalogs 
    assert expected_catalog_config_to_be_added in mock_config_file.catalogs

    calls = []
    for test_catalog in test_default_catalogs:
        calls.append(call(test_catalog))
    calls.append(call(expected_catalog_config_to_be_added))

    mock_DevEnvCatalog.assert_has_calls(calls)
    mock_config_file.flush.assert_called_once()

@patch.object(dev_env_catalog.Core, "user_output")
@patch("dem.core.dev_env_catalog.DevEnvCatalog")
def test_DevEnvCatalogs_add_catalog_exception(mock_DevEnvCatalog: MagicMock, 
                                              mock_user_output: MagicMock):
    # Test setup
    mock_config_file = MagicMock()
    mock_config_file.catalogs = []
    expected_catalog_config_to_be_added = {
        "url": "test_url"
    }

    test_exception_text = "test_exception_text"
    mock_DevEnvCatalog.side_effect = Exception(test_exception_text)

    test_dev_env_catalogs = dev_env_catalog.DevEnvCatalogs(mock_config_file)

    # Run unit under test
    test_dev_env_catalogs.add_catalog(expected_catalog_config_to_be_added)

    # Check expectations
    mock_DevEnvCatalog.assert_called_once_with(expected_catalog_config_to_be_added)
    calls = [
        call(test_exception_text),
        call("Error: Couldn't add this Development Environment Catalog.")
    ]
    mock_user_output.error.assert_has_calls(calls)

@patch("dem.core.dev_env_catalog.DevEnvCatalog")
def test_DevEnvCatalogs_list_catalog_configs(mock_DevEnvCatalog: MagicMock):
    # Test setup
    mock_config_file = MagicMock()
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

    test_dev_env_catalogs = dev_env_catalog.DevEnvCatalogs(mock_config_file)

    # Run unit under test
    actual_catalog_configs = test_dev_env_catalogs.list_catalog_configs()

    # Check expectations
    assert actual_catalog_configs is mock_config_file.catalogs

    calls = []
    for test_catalog in mock_config_file.catalogs:
        calls.append(call(test_catalog))
    mock_DevEnvCatalog.assert_has_calls(calls)

@patch("dem.core.dev_env_catalog.DevEnvCatalog")
def test_DevEnvCatalogs_delete_catalog(mock_DevEnvCatalog: MagicMock):
    # Test setup
    mock_config_file = MagicMock()
    catalog_config_to_delete = {
        "url": "test_url_1"
    }
    mock_config_file.catalogs = [
        catalog_config_to_delete,
        {
            "url": "test_url_2"
        }
    ]
    mock_dev_env_catalogs = [MagicMock(), MagicMock()]
    mock_dev_env_catalogs[0].config = mock_config_file.catalogs[0]
    mock_dev_env_catalogs[1].config = mock_config_file.catalogs[1]
    mock_DevEnvCatalog.side_effect = mock_dev_env_catalogs

    test_dev_env_catalogs = dev_env_catalog.DevEnvCatalogs(mock_config_file)

    # Run unit under test
    test_dev_env_catalogs.delete_catalog(mock_config_file.catalogs[0])

    # Check expectations
    assert mock_dev_env_catalogs[0] not in test_dev_env_catalogs.catalogs
    assert catalog_config_to_delete not in mock_config_file.catalogs

    calls = []
    for test_catalog in mock_config_file.catalogs:
        calls.append(call(test_catalog))
    mock_DevEnvCatalog.assert_has_calls(calls)
    mock_config_file.flush.assert_called_once()