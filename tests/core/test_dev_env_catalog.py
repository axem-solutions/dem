"""Unit tests for the Development Environment Catalog."""

import dem.core.dev_env_catalog as dev_env_catalog

from unittest.mock import MagicMock, call, patch

import pytest


@patch.object(dev_env_catalog.Core, "config_file")
@patch("dem.core.dev_env_catalog.DevEnv")
@patch("dem.core.dev_env_catalog.requests.get")
def test_request_dev_envs_builds_dev_envs(
    mock_get: MagicMock,
    mock_dev_env_class: MagicMock,
    mock_config_file: MagicMock,
) -> None:
    mock_config_file.http_request_timeout_s = 1
    mock_get.return_value.status_code = dev_env_catalog.requests.codes.ok
    descriptors = [{"name": "a"}, {"name": "b"}]
    mock_get.return_value.json.return_value = {"development_environments": descriptors}
    hosts = MagicMock()
    built_dev_envs = [MagicMock(), MagicMock()]
    mock_dev_env_class.side_effect = built_dev_envs
    actual = dev_env_catalog.DevEnvCatalog({"name": "axem", "url": "https://catalog"}, hosts)
    actual.dev_envs = [MagicMock()]

    actual.request_dev_envs()

    assert actual.dev_envs == built_dev_envs
    mock_get.assert_called_once_with("https://catalog", timeout=1)
    mock_dev_env_class.assert_has_calls([call(descriptor, hosts) for descriptor in descriptors])


@patch.object(dev_env_catalog.Core, "config_file")
@patch("dem.core.dev_env_catalog.requests.get")
def test_request_dev_envs_raises_when_request_fails(
    mock_get: MagicMock, mock_config_file: MagicMock
) -> None:
    mock_config_file.http_request_timeout_s = 1
    mock_get.side_effect = Exception("boom")
    actual = dev_env_catalog.DevEnvCatalog({"name": "axem", "url": "https://catalog"}, MagicMock())

    with pytest.raises(dev_env_catalog.CatalogError) as exc_info:
        actual.request_dev_envs()

    assert (
        str(exc_info.value)
        == "Catalog error: Error in communication with the [bold]axem[/bold] Development Environment Catalog.\nboom"
    )


@patch.object(dev_env_catalog.Core, "config_file")
@patch("dem.core.dev_env_catalog.requests.get")
def test_request_dev_envs_raises_for_bad_status(
    mock_get: MagicMock, mock_config_file: MagicMock
) -> None:
    mock_config_file.http_request_timeout_s = 1
    mock_get.return_value.status_code = dev_env_catalog.requests.codes.not_found
    actual = dev_env_catalog.DevEnvCatalog({"name": "axem", "url": "https://catalog"}, MagicMock())

    with pytest.raises(dev_env_catalog.CatalogError) as exc_info:
        actual.request_dev_envs()

    assert "Failed to retrieve Development Environments." in str(exc_info.value)


@patch.object(dev_env_catalog.Core, "config_file")
@patch("dem.core.dev_env_catalog.DevEnv")
@patch("dem.core.dev_env_catalog.requests.get")
def test_request_dev_envs_raises_for_corrupted_catalog(
    mock_get: MagicMock,
    mock_dev_env_class: MagicMock,
    mock_config_file: MagicMock,
) -> None:
    mock_config_file.http_request_timeout_s = 1
    mock_get.return_value.status_code = dev_env_catalog.requests.codes.ok
    mock_get.return_value.json.return_value = {"development_environments": [{"name": "a"}]}
    mock_dev_env_class.side_effect = Exception("broken descriptor")
    actual = dev_env_catalog.DevEnvCatalog({"name": "axem", "url": "https://catalog"}, MagicMock())

    with pytest.raises(dev_env_catalog.CatalogError) as exc_info:
        actual.request_dev_envs()

    assert (
        str(exc_info.value)
        == "Catalog error: The axem Development Environment Catalog is corrupted.\nbroken descriptor"
    )


def test_get_dev_env_by_name_returns_match() -> None:
    actual = dev_env_catalog.DevEnvCatalog({"name": "axem", "url": "https://catalog"}, MagicMock())
    matching_dev_env = MagicMock()
    matching_dev_env.name = "demo"
    actual.dev_envs = [matching_dev_env]

    assert actual.get_dev_env_by_name("demo") is matching_dev_env
    assert actual.get_dev_env_by_name("missing") is None


@patch.object(dev_env_catalog.Core, "config_file")
@patch("dem.core.dev_env_catalog.DevEnvCatalog")
def test_dev_env_catalogs_build_catalog_instances(
    mock_catalog_class: MagicMock, mock_config_file: MagicMock
) -> None:
    mock_config_file.catalogs = [{"name": "axem", "url": "https://catalog"}]
    hosts = MagicMock()

    actual = dev_env_catalog.DevEnvCatalogs(hosts)

    assert actual.catalogs == [mock_catalog_class.return_value]
    mock_catalog_class.assert_called_once_with(mock_config_file.catalogs[0], hosts)


@patch("dem.core.dev_env_catalog.DevEnvCatalog")
def test_add_catalog_validates_and_flushes(mock_catalog_class: MagicMock) -> None:
    hosts = MagicMock()
    actual = dev_env_catalog.DevEnvCatalogs.__new__(dev_env_catalog.DevEnvCatalogs)
    actual.hosts = hosts
    actual.catalogs = []
    actual.config_file = MagicMock()
    actual.config_file.catalogs = []
    new_catalog = MagicMock()
    mock_catalog_class.return_value = new_catalog

    actual.add_catalog("axem", "https://catalog")

    mock_catalog_class.assert_called_once_with({"name": "axem", "url": "https://catalog"}, hosts)
    new_catalog.request_dev_envs.assert_called_once()
    assert actual.catalogs == [new_catalog]
    assert actual.config_file.catalogs == [{"name": "axem", "url": "https://catalog"}]
    actual.config_file.flush.assert_called_once()


def test_delete_catalog_removes_existing_entry() -> None:
    actual = dev_env_catalog.DevEnvCatalogs.__new__(dev_env_catalog.DevEnvCatalogs)
    actual.config_file = MagicMock()
    actual.config_file.catalogs = [{"name": "axem", "url": "https://catalog"}]
    catalog = MagicMock()
    catalog.name = "axem"
    catalog.config = actual.config_file.catalogs[0]
    actual.catalogs = [catalog]

    actual.delete_catalog("axem")

    assert actual.catalogs == []
    assert actual.config_file.catalogs == []
    actual.config_file.flush.assert_called_once()


def test_delete_catalog_raises_for_missing_entry() -> None:
    actual = dev_env_catalog.DevEnvCatalogs.__new__(dev_env_catalog.DevEnvCatalogs)
    actual.config_file = MagicMock()
    actual.catalogs = []

    with pytest.raises(dev_env_catalog.CatalogError) as exc_info:
        actual.delete_catalog("missing")

    assert (
        str(exc_info.value)
        == "Catalog error: The missing Development Environment Catalog doesn't exist."
    )
