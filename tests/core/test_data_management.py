"""Unit tests for the data_management."""
# tests/core/test_data_management.py

# Unit under test:
import dem.core.data_management as data_management

# Test framework
from unittest.mock import patch, MagicMock, call

import json.decoder

## Test cases

@patch("dem.core.data_management.open")
@patch("dem.core.data_management.json.load")
def test_BaseJSON_existing_json(mock_json_load: MagicMock, mock_open: MagicMock):
    # Test setup
    fake_opened_file = MagicMock()
    mock_open.return_value = fake_opened_file
    expected_deserialized_json = MagicMock()
    mock_json_load.return_value = expected_deserialized_json

    test_path = "test_path"
    data_management.BaseJSON._path = test_path

    # Run unit under test
    base_json = data_management.BaseJSON()

    # Check expectations
    mock_open.assert_called_once_with(test_path, "r")
    mock_json_load.assert_called_once_with(fake_opened_file)
    fake_opened_file.close.assert_called_once()

    assert base_json.deserialized is expected_deserialized_json

@patch("dem.core.data_management.open")
@patch("dem.core.data_management.json.loads")
@patch("dem.core.data_management.os.path.exists")
@patch("dem.core.data_management.os.makedirs")
def test_dev_env_json_read_FileNotFounderror(mock_os_makedirs: MagicMock, 
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

    # Run unit under test
    base_json = data_management.BaseJSON()
   
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

@patch.object(data_management.BaseJSON, "_create_default_json")
@patch("dem.core.data_management.open")
@patch("dem.core.data_management.json.load")
def test_dev_env_json_read_JSONDecodeError(mock_json_load: MagicMock, mock_open: MagicMock, 
                                           mock_create_default_json: MagicMock):
    # Test setup
    fake_opened_file = MagicMock()
    mock_open.return_value = fake_opened_file
    mock_json_load.side_effect = json.decoder.JSONDecodeError("dummy_msg", "dummy_doc", 0)

    mock_deserialized = MagicMock()
    mock_create_default_json.return_value = mock_deserialized

    data_management.BaseJSON.user_output = MagicMock()

    # Run unit under test
    base_json =  data_management.BaseJSON()

    # Check expectations
    mock_open.assert_called_once_with(base_json._path, "r")
    mock_json_load.assert_called_once_with(fake_opened_file)

    base_json.user_output.get_confirm.assert_called_once_with("[red]Error: invalid json format.[/]", 
                                                              "Restore the original json file?")
    mock_create_default_json.assert_called_once()

    assert base_json.deserialized is mock_deserialized

@patch.object(data_management.BaseJSON, "update", MagicMock())
@patch("dem.core.data_management.open")
@patch("dem.core.data_management.json.dump")
def test_dev_env_json_write(mock_json_dump: MagicMock, mock_open: MagicMock):
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

@patch("dem.core.data_management.PurePath")
def test_ConfigFile(mock_PurePath: MagicMock):
    # Test setup
    mock_pure_path = MagicMock()
    mock_PurePath.return_value = mock_pure_path

    test_path = "test_path"
    data_management.BaseJSON._config_dir = test_path

    mock_registries = MagicMock()
    mock_catalogs = MagicMock()
    def stub_update(self):
        self.deserialized["registries"] = mock_registries
        self.deserialized["catalogs"] = mock_catalogs
    data_management.BaseJSON.update = stub_update

    # Run unit under test
    local_dev_env_json = data_management.ConfigFile()

    # Check expectations
    assert local_dev_env_json._path is mock_pure_path
    assert local_dev_env_json._default_json == """{
    "registries": [],
    "catalogs": []
}"""
    assert local_dev_env_json.registries is mock_registries
    assert local_dev_env_json.catalogs is mock_catalogs

    mock_PurePath.assert_called_once_with(test_path + "/config.json")