"""Unit tests for the data_management."""
# tests/core/test_data_management.py

# Unit under test:
from dem.core.data_management import LocalDevEnvJSON, OrgDevEnvJSON, _empty_dev_env_json

# Test framework
from unittest.mock import patch, MagicMock, call

from pathlib import PurePath
import os

## Test cases


@patch("dem.core.data_management.open")
@patch("dem.core.data_management.json.load")
def test_dev_env_json_read(mock_json_load, mock_open):
    # Test setup
    fake_opened_file = MagicMock()
    mock_open.return_value = fake_opened_file
    expected_deserialized_dev_env_json = MagicMock()
    mock_json_load.return_value = expected_deserialized_dev_env_json

    # Run unit under test
    dev_env_json = LocalDevEnvJSON()
    deserialized_dev_env_json = dev_env_json.read()

    # Check expectations
    mock_open.assert_called_once_with(PurePath(os.path.expanduser('~') + "/.config/axem/dev_env.json"), "r")
    mock_json_load.assert_called_once_with(fake_opened_file)
    fake_opened_file.close.assert_called_once()

    assert deserialized_dev_env_json is expected_deserialized_dev_env_json

@patch("dem.core.data_management.open")
@patch("dem.core.data_management.json.loads")
@patch("dem.core.data_management.os.path.exists")
@patch("dem.core.data_management.os.makedirs")
def test_dev_env_json_read_FileNotFounderror(mock_os_makedirs, mock_os_path, mock_json_loads, mock_open):
    # Test setup
    fake_opened_file = MagicMock()
    mock_open.side_effect = [FileNotFoundError, fake_opened_file]
    expected_deserialized_dev_env_json = MagicMock()
    mock_json_loads.return_value = expected_deserialized_dev_env_json
    mock_os_path.return_value = False

    # Run unit under test
    dev_env_json = LocalDevEnvJSON()
    deserialized_dev_env_json = dev_env_json.read()
   
    # Check expectations
    calls = [
        call(PurePath(os.path.expanduser('~') + "/.config/axem/dev_env.json"), "r"),
        call(PurePath(os.path.expanduser('~') + "/.config/axem/dev_env.json"), "w"),
    ]

    mock_open.assert_has_calls(calls)
    
    fake_opened_file.write.assert_called_once_with(_empty_dev_env_json)    
    fake_opened_file.close.assert_called_once()
  
    mock_os_path.assert_called_once()
    mock_os_makedirs.assert_called_once_with(dev_env_json._directory)
    
    mock_json_loads.assert_called_once_with(_empty_dev_env_json)

    assert deserialized_dev_env_json is expected_deserialized_dev_env_json

@patch("dem.core.data_management.open")
@patch("dem.core.data_management.json.dump")
def test_dev_env_json_write(mock_json_dump, mock_open):
    # Test setup
    fake_opened_file = MagicMock()
    mock_open.return_value = fake_opened_file
    fake_dev_env_json_deserialized = MagicMock()

    # Run unit under test
    dev_env_json = LocalDevEnvJSON()
    dev_env_json.write(fake_dev_env_json_deserialized)

    # Check expectations
    mock_open.assert_called_once_with(PurePath(os.path.expanduser('~') + "/.config/axem/dev_env.json"), "w")
    mock_json_dump.assert_called_once_with(fake_dev_env_json_deserialized, fake_opened_file,
                                           indent=4)
    fake_opened_file.close.assert_called_once_with()

@patch("dem.core.data_management.requests.get")
def test_read_deserialized_dev_env_org_json(mock_requests_get):
    # Test setup
    fake_response = MagicMock()
    mock_requests_get.return_value = fake_response
    expected_json = MagicMock()
    fake_response.json.return_value = expected_json

    # Run unit under test
    org_dev_env_json = OrgDevEnvJSON()
    actual_json = org_dev_env_json.read()

    # Check expectations
    assert expected_json == actual_json
    assert expected_json == org_dev_env_json.deserialized