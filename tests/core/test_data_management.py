"""Unit tests for the data_management."""
# tests/core/test_data_management.py

# Unit under test:
import dem.core.data_management as data_management

# Test framework
from unittest.mock import patch, MagicMock

## Test cases

@patch("dem.core.data_management.PurePath")
@patch("dem.core.data_management.open")
@patch("dem.core.data_management.json.load")
def test_deserialize_dev_env_json(mock_json_load, mock_open, mock_PurePath):
    mock_PurePath.return_value = "test_path"
    fake_opened_file = MagicMock()
    mock_open.return_value = fake_opened_file
    expected_deserialized_dev_env_json = MagicMock()
    mock_json_load.return_value = expected_deserialized_dev_env_json

    deserialized_dev_env_json = data_management.read_deserialized_dev_env_json()

    mock_open.assert_called_once_with(mock_PurePath.return_value, "r")
    mock_json_load.assert_called_once_with(fake_opened_file)
    fake_opened_file.close.assert_called_once_with()

    assert deserialized_dev_env_json is expected_deserialized_dev_env_json

@patch("dem.core.data_management.PurePath")
@patch("dem.core.data_management.open")
@patch("dem.core.data_management.json.dump")
def test_serialize_dev_env_json(mock_json_dump, mock_open, mock_PurePath):
    mock_PurePath.return_value = "test_path"
    fake_opened_file = MagicMock()
    mock_open.return_value = fake_opened_file
    fake_dev_env_json_deserialized = MagicMock()

    data_management.write_deserialized_dev_env_json(fake_dev_env_json_deserialized)

    mock_open.assert_called_once_with(mock_PurePath.return_value, "w")
    mock_json_dump.assert_called_once_with(fake_dev_env_json_deserialized, fake_opened_file,
                                           indent=4)
    fake_opened_file.close.assert_called_once_with()