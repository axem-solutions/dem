"""Test cases for the Hosts."""
# tests/core/test_hosts.py

# Unit under test:
import dem.core.hosts as hosts

# Test framework
from unittest.mock import patch, MagicMock, call

## Test cases

def test_Host() -> None:
    # Test setup
    test_host_config: dict[str, str] = {
        "name": "test_name",
        "address": "test_address"
    }

    # Run unit under test
    test_host = hosts.Host(test_host_config)

    # Check expectations
    assert test_host.name == test_host_config["name"]
    assert test_host.address == test_host_config["address"]
    assert test_host.config == test_host_config

@patch.object(hosts.Core, "config_file")
def test_Hosts(mock_config_file) -> None:
    # Test setup
    test_host_configs: list[dict[str, str]] = [
        {
            "name": "test_name1",
            "address": "test_address1"
        },
        {
            "name": "test_name2",
            "address": "test_address2"
        }
    ]
    mock_config_file.hosts = test_host_configs

    # Run unit under test
    test_hosts = hosts.Hosts()

    # Check expectations
    assert len(test_hosts.hosts) == len(test_host_configs)

    for index, test_host_config in enumerate(test_host_configs):
        assert test_hosts.hosts[index].name == test_host_config["name"]
        assert test_hosts.hosts[index].address == test_host_config["address"]
        assert test_hosts.hosts[index].config == test_host_config

@patch.object(hosts.Core, "config_file")
@patch.object(hosts.Core, "user_output")
@patch("dem.core.hosts.Host")
def test_Hosts_error(mock_Host: MagicMock, mock_user_output: MagicMock, mock_config_file: MagicMock) -> None:
    # Test setup
    test_host_config: list[dict[str, str]] = [
        {
            "name": "test_name1",
            "address": "test_address1"
        }
    ]
    mock_config_file.hosts = test_host_config

    test_exception_text = "test_exception_text"
    mock_Host.side_effect = Exception(test_exception_text)

    # Run unit under test
    test_hosts = hosts.Hosts()

    # Check expectations
    assert len(test_hosts.hosts) == 0

    mock_Host.assert_called_once_with(test_host_config[0])
    mock_user_output.assert_has_calls([
        call.error(test_exception_text),
        call.error("Error: Couldn't add this Host.")
    ])

@patch.object(hosts.Core, "config_file")
@patch.object(hosts.Hosts, "_try_to_add_host")
@patch.object(hosts.Hosts, "__init__")
def test_Hosts_add_host(mock___init__: MagicMock, mock__try_to_add_host: MagicMock, 
                        mock_config_file: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    mock_config_file.hosts = []

    test_host_config: dict[str, str] = {
        "name": "test_name",
        "address": "test_address"
    }

    test_hosts = hosts.Hosts()

    # Run unit under test
    test_hosts.add_host(test_host_config)

    # Check expectations
    assert test_host_config in mock_config_file.hosts

    mock___init__.assert_called_once()
    mock__try_to_add_host.assert_called_once_with(test_host_config)
    mock_config_file.flush.assert_called_once()

@patch.object(hosts.Core, "config_file")
@patch.object(hosts.Hosts, "__init__")
def test_Hosts_list_host_configs(mock___init__: MagicMock, mock_config_file: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    mock_hosts = MagicMock()
    mock_config_file.hosts = mock_hosts

    test_hosts = hosts.Hosts()

    # Run unit under test
    actual_hosts: list = test_hosts.list_host_configs()

    # Check expectations
    assert actual_hosts is mock_hosts

    mock___init__.assert_called_once()

@patch.object(hosts.Core, "config_file")
@patch.object(hosts.Hosts, "__init__")
def test_Hosts_delete_host(mock___init__: MagicMock, mock_config_file: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_host_config: dict[str, str] = {
        "name": "test_name",
        "address": "test_address"
    }
    mock_config_file.hosts = [test_host_config]

    mock_host = MagicMock()
    mock_host.config = test_host_config

    test_hosts = hosts.Hosts()
    test_hosts.hosts = [mock_host]

    # Run unit under test
    test_hosts.delete_host(test_host_config)

    # Check expectations
    assert test_host_config not in mock_config_file.hosts
    assert mock_host not in test_hosts.hosts

    mock___init__.assert_called_once()
    mock_config_file.flush.assert_called_once()