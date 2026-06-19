"""Unit tests for hosts."""

import dem.core.hosts as hosts

from unittest.mock import MagicMock, patch


@patch("dem.core.hosts.ContainerEngine")
def test_host_initializes_container_engine(mock_container_engine: MagicMock) -> None:
    actual = hosts.Host({"name": "remote", "address": "tcp://remote"})

    assert actual.name == "remote"
    assert actual.address == "tcp://remote"
    assert actual.container_engine is mock_container_engine.return_value
    mock_container_engine.assert_called_once_with("tcp://remote")


@patch.object(hosts.Core, "config_file")
@patch("dem.core.hosts.Host")
def test_hosts_initializes_local_and_remotes(mock_host_class: MagicMock, mock_config_file: MagicMock) -> None:
    mock_config_file.hosts = [
        {"name": "remote-a", "address": "tcp://a"},
        {"name": "remote-b", "address": "tcp://b"},
    ]
    local_host = MagicMock()
    local_host.name = "local"
    remote_a = MagicMock()
    remote_a.name = "remote-a"
    remote_b = MagicMock()
    remote_b.name = "remote-b"
    mock_host_class.side_effect = [local_host, remote_a, remote_b]

    actual = hosts.Hosts()

    assert actual.local is local_host
    assert actual.remotes == {"remote-a": remote_a, "remote-b": remote_b}
    actual.local.container_engine.start.assert_called_once()


@patch("dem.core.hosts.Host")
@patch.object(hosts.Hosts, "__init__", return_value=None)
def test_add_host_updates_remotes_and_config(mock_init: MagicMock, mock_host_class: MagicMock) -> None:
    actual = hosts.Hosts()
    actual.remotes = {}
    actual.config_file = MagicMock()
    actual.config_file.hosts = []
    remote_host = MagicMock()
    remote_host.name = "remote-a"
    mock_host_class.return_value = remote_host
    host_config = {"name": "remote-a", "address": "tcp://a"}

    actual.add_host(host_config)

    assert actual.remotes == {"remote-a": remote_host}
    assert actual.config_file.hosts == [host_config]
    actual.config_file.flush.assert_called_once()


@patch.object(hosts.Hosts, "__init__", return_value=None)
def test_list_host_configs_returns_config(mock_init: MagicMock) -> None:
    actual = hosts.Hosts()
    actual.config_file = MagicMock()
    actual.config_file.hosts = [{"name": "remote-a", "address": "tcp://a"}]

    assert actual.list_host_configs() == [{"name": "remote-a", "address": "tcp://a"}]


@patch.object(hosts.Hosts, "__init__", return_value=None)
def test_delete_host_updates_remotes_and_config(mock_init: MagicMock) -> None:
    actual = hosts.Hosts()
    actual.remotes = {"remote-a": MagicMock()}
    actual.config_file = MagicMock()
    host_config = {"name": "remote-a", "address": "tcp://a"}
    actual.config_file.hosts = [host_config]

    actual.delete_host(host_config)

    assert actual.remotes == {}
    assert actual.config_file.hosts == []
    actual.config_file.flush.assert_called_once()


@patch.object(hosts.Hosts, "__init__", return_value=None)
def test_get_host_by_name_returns_local_and_remote(mock_init: MagicMock) -> None:
    actual = hosts.Hosts()
    actual.local = MagicMock()
    remote_host = MagicMock()
    actual.remotes = {"remote-a": remote_host}

    assert actual.get_host_by_name("local") is actual.local
    assert actual.get_host_by_name("remote-a") is remote_host
    assert actual.get_host_by_name("missing") is None
