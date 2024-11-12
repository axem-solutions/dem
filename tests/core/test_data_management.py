"""Unit tests for the data_management."""
# tests/core/test_data_management.py

# Unit under test:
import dem.core.data_management as data_management

# Test framework
from unittest.mock import patch, MagicMock, call
import pytest

import json.decoder

## Test cases

@patch("dem.core.data_management.open")
@patch("dem.core.data_management.json.load")
def test_BaseJSON_update(mock_json_load: MagicMock, mock_open: MagicMock) -> None:
    # Test setup
    fake_opened_file = MagicMock()
    mock_open.return_value = fake_opened_file
    expected_deserialized_json = MagicMock()
    mock_json_load.return_value = expected_deserialized_json

    test_path = "test_path"
    data_management.BaseJSON._path = test_path
    base_json = data_management.BaseJSON()

    # Run unit under test
    base_json.update()

    # Check expectations
    mock_open.assert_called_once_with(test_path, "r")
    mock_json_load.assert_called_once_with(fake_opened_file)
    fake_opened_file.close.assert_called_once()

    assert base_json.deserialized is expected_deserialized_json

@patch("dem.core.data_management.open")
@patch("dem.core.data_management.json.loads")
@patch("dem.core.data_management.os.path.exists")
@patch("dem.core.data_management.os.makedirs")
def test_BaseJSON_update_FileNotFoundError(mock_os_makedirs: MagicMock, 
                                           mock_os_path_exists: MagicMock, 
                                           mock_json_loads: MagicMock, 
                                           mock_open: MagicMock):
    # Test setup
    fake_opened_file = MagicMock()
    mock_open.side_effect = [FileNotFoundError, fake_opened_file]
    expected_deserialized_json = MagicMock()
    mock_json_loads.return_value = expected_deserialized_json
    mock_os_path_exists.return_value = False

    test_default_json = "test_empty_json"
    data_management.BaseJSON._default_json = test_default_json
    base_json = data_management.BaseJSON()

    # Run unit under test
    base_json.update()
   
    # Check expectations
    calls = [
        call(base_json._path, "r"),
        call(base_json._path, "w"),
    ]
    mock_open.assert_has_calls(calls)
    
    fake_opened_file.write.assert_called_once_with(test_default_json)    
    fake_opened_file.close.assert_called_once()
  
    mock_os_path_exists.assert_called_once()
    mock_os_makedirs.assert_called_once_with(base_json._config_dir)
    
    mock_json_loads.assert_called_once_with(test_default_json)

    assert base_json.deserialized is expected_deserialized_json

@patch("dem.core.data_management.open")
@patch("dem.core.data_management.json.dump")
def test_BaseJSON_flush(mock_json_dump: MagicMock, mock_open: MagicMock) -> None:
    # Test setup
    mock_opened_file = MagicMock()
    mock_open.return_value = mock_opened_file
    fake_json_deserialized = MagicMock()

    base_json = data_management.BaseJSON()
    base_json.deserialized = fake_json_deserialized

    # Run unit under test
    base_json.flush()

    # Check expectations
    mock_open.assert_called_once_with(base_json._path, "w")
    mock_json_dump.assert_called_once_with(fake_json_deserialized, mock_opened_file, indent=4)
    mock_opened_file.close.assert_called_once()

@patch.object(data_management.BaseJSON, "_create_default_json")
def test_BaseJSON_restore(mock_create_default_json: MagicMock) -> None:
    # Test setup
    mock_json_deserialized = MagicMock()
    mock_create_default_json.return_value = mock_json_deserialized

    test_base_json = data_management.BaseJSON()

    # Run unit under test
    test_base_json.restore()

    # Check expectations
    assert test_base_json.deserialized is mock_json_deserialized

    mock_create_default_json.assert_called_once()

@patch("dem.core.data_management.PurePath")
@patch.object(data_management.BaseJSON, "__init__")
def test_LocalDevEnvJSON(mock___init__: MagicMock, mock_PurePath: MagicMock):
    # Test setup
    mock_pure_path = MagicMock()
    mock_PurePath.return_value = mock_pure_path

    test_path = "test_path"
    data_management.BaseJSON._config_dir = test_path

    # Run unit under test
    local_dev_env_json = data_management.LocalDevEnvJSON()

    # Check expectations
    assert local_dev_env_json._path is mock_pure_path
    assert local_dev_env_json._default_json == """{
    "version": "0.1",
    "org_name": "axem",
    "registry": "registry-1.docker.io",
    "development_environments": []
}
"""

    mock_PurePath.assert_called_once_with(test_path + "/dev_env.json")
    mock___init__.assert_called_once()

@patch.object(data_management.BaseJSON, "update")
def test_LocalDevEnvJSON_update(mock_update: MagicMock) -> None:
    # Test setup
    test_local_dev_env_json = data_management.LocalDevEnvJSON()

    # Run unit under test
    test_local_dev_env_json.update()

    # Check expectations
    mock_update.assert_called_once()

@patch.object(data_management.BaseJSON, "update")
def test_LocalDevEnvJSON_update_JSONDecodeError(mock_update: MagicMock) -> None:
    # Test setup
    test_local_dev_env_json = data_management.LocalDevEnvJSON()
    mock_update.side_effect = json.decoder.JSONDecodeError("test_msg", "test_doc", 0)

    with pytest.raises(data_management.DataStorageError) as e:
        # Run unit under test
        test_local_dev_env_json.update()

    # Check expectations
    assert "Invalid file: The dev_env.json file is corrupted.\ntest_msg: line 1 column 1 (char 0)" == str(e.value)

    mock_update.assert_called_once()

@patch("dem.core.data_management.PurePath")
def test_ConfigFile(mock_PurePath: MagicMock):
    # Test setup
    mock_pure_path = MagicMock()
    mock_PurePath.return_value = mock_pure_path

    test_path = "test_path"
    data_management.BaseJSON._config_dir = test_path

    # Run unit under test
    local_dev_env_json = data_management.ConfigFile()

    # Check expectations
    assert local_dev_env_json._path is mock_pure_path
    assert local_dev_env_json._default_json == """{
    "registries": [
        {
            "name": "axem",
            "namespace": "axemsolutions",
            "url": "https://registry.hub.docker.com"
        }
    ],
    "catalogs": [
        {
            "name": "axem",
            "url": "https://axemsolutions.io/dem/dev_env_org.json"
        }
    ],
    "hosts": [],
    "http_request_timeout_s": 2,
    "use_native_system_cert_store": false
}"""

    mock_PurePath.assert_called_once_with(test_path + "/config.json")

@patch.object(data_management.BaseJSON, "flush")
@patch.object(data_management.BaseJSON, "update")
def test_ConfigFile_update(mock_update: MagicMock, mock_flush: MagicMock) -> None:
    # Test setup
    test_config_file = data_management.ConfigFile()
    test_registry = MagicMock()
    test_catalog = MagicMock()
    test_host = MagicMock()
    test_http_request_timeout_s = 2
    test_config_file.deserialized = {
        "registries": [test_registry],
        "catalogs": [test_catalog],
        "hosts": [test_host],
        "http_request_timeout_s": test_http_request_timeout_s
    }

    # Run unit under test
    test_config_file.update()

    # Check expectations
    assert test_registry in test_config_file.registries
    assert test_catalog in test_config_file.catalogs
    assert test_host in test_config_file.hosts
    assert test_config_file.http_request_timeout_s == test_http_request_timeout_s

    mock_update.assert_called_once()
    mock_flush.assert_called_once()

@patch.object(data_management.BaseJSON, "update")
def test_ConfigFile_update_JSONDecodeError(mock_update: MagicMock) -> None:
    # Test setup
    test_config_file = data_management.ConfigFile()
    mock_update.side_effect = json.decoder.JSONDecodeError("test_msg", "test_doc", 0)

    with pytest.raises(data_management.DataStorageError) as e:
        # Run unit under test
        test_config_file.update()

    # Check expectations
    assert "Invalid file: The config.json file is corrupted.\ntest_msg: line 1 column 1 (char 0)" == str(e.value)

    mock_update.assert_called_once()