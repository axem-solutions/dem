"""Unit tests for the Development Platform."""
# tests/core/test_platform.py

# Unit under test:
import dem.core.platform as platform

# Test framework
import pytest
from unittest.mock import patch, MagicMock, call

from dem.core.exceptions import InvalidDevEnvJson
from typing import Any

@patch("dem.core.platform.DevEnv")
@patch("dem.core.platform.LocalDevEnvJSON")
def test_Platform_creation(mock_LocalDevEnvJSON: MagicMock, mock_DevEnv: MagicMock) -> None:
    # Test setup
    mock_local_dev_env_json = MagicMock()
    mock_LocalDevEnvJSON.return_value = mock_local_dev_env_json
    mock_dev_env = MagicMock()
    mock_DevEnv.return_value = mock_dev_env
    test_major_version = 0
    platform.__supported_dev_env_major_version__ = test_major_version
    test_dev_env_descriptor = {
        "name": "test_dev_env_name"
    }
    mock_local_dev_env_json.deserialized = {
        "version": "0.0",
        "development_environments": [
            test_dev_env_descriptor
        ]
    }

    # Run unit under test
    test_platform = platform.Platform()

    # Check expectations
    mock_LocalDevEnvJSON.assert_called_once()
    mock_DevEnv.assert_called_once_with(descriptor=test_dev_env_descriptor)

    assert test_platform.local_dev_envs[0] is mock_dev_env
    assert test_platform.version == mock_local_dev_env_json.deserialized["version"]

@patch("dem.core.platform.LocalDevEnvJSON")
def test_Platfrom_invalid_version_expect_error(mock_LocalDevEnvJSON: MagicMock) -> None:
    # Test setup
    mock_local_dev_env_json = MagicMock()
    mock_LocalDevEnvJSON.return_value = mock_local_dev_env_json
    test_major_version = 1
    platform.__supported_dev_env_major_version__ = test_major_version
    mock_local_dev_env_json.deserialized = {
        "version": "0.0"
    }

    # Run unit under test
    with pytest.raises(InvalidDevEnvJson) as exported_exception_info:
        platform.Platform()

    # Check expectations
    excepted_error_message = "Error in dev_env.json: The dev_env.json version v1.0 is not supported."
    assert str(exported_exception_info.value) == excepted_error_message

@patch("dem.core.platform.ToolImages")
@patch.object(platform.Platform, "__init__")
def test_Platform_tool_images(mock___init__: MagicMock, mock_ToolImages: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    mock_container_engine = MagicMock()
    mock_registries = MagicMock()
    test_update_tool_images_on_instantiation = True

    test_platform = platform.Platform()
    test_platform._container_engine = mock_container_engine
    test_platform._registries = mock_registries
    test_platform.update_tool_images_on_instantiation = test_update_tool_images_on_instantiation
    test_platform._tool_images = None

    mock_tool_images = MagicMock()
    mock_ToolImages.return_value = mock_tool_images

    # Run unit under test
    actual_tool_images = test_platform.tool_images

    # Check expectations
    assert actual_tool_images is mock_tool_images
    assert test_platform._tool_images is mock_tool_images

    mock___init__.assert_called_once()
    mock_ToolImages.assert_called_once_with(mock_container_engine, mock_registries, 
                                            test_update_tool_images_on_instantiation)

@patch("dem.core.platform.ContainerEngine")
@patch.object(platform.Platform, "__init__")
def test_Platform_container_engine(mock___init__: MagicMock, mock_ContainerEngine: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_platform = platform.Platform()
    test_platform._container_engine = None

    mock_container_engine = MagicMock()
    mock_ContainerEngine.return_value = mock_container_engine

    # Run unit under test
    actual_container_engine = test_platform.container_engine

    # Check expectations
    assert actual_container_engine is mock_container_engine
    assert test_platform._container_engine is mock_container_engine

    mock___init__.assert_called_once()
    mock_ContainerEngine.assert_called_once()

@patch("dem.core.platform.Registries")
@patch.object(platform.Platform, "__init__")
def test_Platform_registries(mock___init__: MagicMock, mock_Registries: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_platform = platform.Platform()
    test_platform._registries = None

    mock_container_engine = MagicMock()
    mock_config_file = MagicMock()
    test_platform._container_engine = mock_container_engine
    test_platform._config_file = mock_config_file

    mock_registries = MagicMock()
    mock_Registries.return_value = mock_registries

    # Run unit under test
    actual_registries = test_platform.registries

    # Check expectations
    assert actual_registries is mock_registries
    assert test_platform._registries is mock_registries

    mock___init__.assert_called_once()
    mock_Registries.assert_called_once_with(mock_container_engine, mock_config_file)

@patch("dem.core.platform.ConfigFile")
@patch.object(platform.Platform, "__init__")
def test_Platform_config_file(mock___init__: MagicMock, mock_ConfigFile: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_platform = platform.Platform()
    test_platform._config_file = None

    mock_config_file = MagicMock()
    mock_ConfigFile.return_value = mock_config_file

    # Run unit under test
    actual_config_file = test_platform.config_file

    # Check expectations
    assert actual_config_file is mock_config_file
    assert test_platform._config_file is mock_config_file

    mock___init__.assert_called_once()
    mock_ConfigFile.assert_called_once()

@patch("dem.core.platform.DevEnvCatalogs")
@patch.object(platform.Platform, "__init__")
def test_Platform_dev_env_catalogs(mock___init__: MagicMock, mock_DevEnvCatalogs: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_platform = platform.Platform()
    test_platform._dev_env_catalogs = None

    mock_config_file = MagicMock()
    test_platform._config_file = mock_config_file

    mock_dev_env_catalogs = MagicMock()
    mock_DevEnvCatalogs.return_value = mock_dev_env_catalogs

    # Run unit under test
    actual_dev_env_catalogs = test_platform.dev_env_catalogs

    # Check expectations
    assert actual_dev_env_catalogs is mock_dev_env_catalogs
    assert test_platform._dev_env_catalogs is mock_dev_env_catalogs

    mock___init__.assert_called_once()
    mock_DevEnvCatalogs.assert_called_once_with(mock_config_file)

@patch("dem.core.platform.Hosts")
@patch.object(platform.Platform, "__init__")
def test_Platform_hosts(mock___init__: MagicMock, mock_Hosts: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_platform = platform.Platform()
    test_platform._hosts = None

    mock_config_file = MagicMock()
    test_platform._config_file = mock_config_file

    mock_hosts = MagicMock()
    mock_Hosts.return_value = mock_hosts

    # Run unit under test
    actual_hosts = test_platform.hosts

    # Check expectations
    assert actual_hosts is mock_hosts
    assert test_platform._hosts is mock_hosts

    mock___init__.assert_called_once()
    mock_Hosts.assert_called_once_with(mock_config_file)

@patch.object(platform.Platform, "__init__")
def test_Platform_get_deserialized(mock___init__: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None
    
    test_plaform = platform.Platform()
    test_plaform.version = "0.0"

    mock_dev_env1 = MagicMock()
    mock_dev_env2 = MagicMock()

    test_deser_dev_env_1: dict[str, Any]= {
        "name": "test_dev_env_name1",
        "installed": "True",
        "tools": []
    }
    mock_dev_env1.get_deserialized.return_value = test_deser_dev_env_1

    test_deser_dev_env_2: dict[str, Any]= {
        "name": "test_dev_env_name2",
        "installed": "True",
        "tools": []
    }
    mock_dev_env2.get_deserialized.return_value = test_deser_dev_env_2

    test_plaform.local_dev_envs = [
        mock_dev_env1, mock_dev_env2
    ]

    # Run unit under test
    actual_deserialized = test_plaform.get_deserialized()

    # Check expectations
    expected_deserialized = {
        "version": test_plaform.version,
        "development_environments": [
            test_deser_dev_env_1, test_deser_dev_env_2
        ]
    }
    assert actual_deserialized == expected_deserialized

    mock___init__.assert_called_once()

@patch.object(platform.Platform, "__init__")
def test_Platform_get_dev_env_by_name_match(mock___init__: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None
    
    test_plaform = platform.Platform()
    test_name = "dev_env_name"
    expected_dev_env = MagicMock()
    expected_dev_env.name = test_name
    test_plaform.local_dev_envs = [expected_dev_env]

    # Run unit under test
    actual_dev_env = test_plaform.get_dev_env_by_name(test_name)

    # Check expectations
    assert actual_dev_env == expected_dev_env

    mock___init__.assert_called_once()

@patch.object(platform.Platform, "__init__")
def test_Platform_get_dev_env_by_name_no_match(mock___init__: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None
    
    test_plaform = platform.Platform()
    test_name = "dev_env_name"
    expected_dev_env = MagicMock()
    expected_dev_env.name = test_name
    test_plaform.local_dev_envs = [expected_dev_env]

    # Run unit under test
    actual_dev_env = test_plaform.get_dev_env_by_name("not_existing_name")

    # Check expectations
    assert actual_dev_env is None

    mock___init__.assert_called_once()

@patch.object(platform.Platform, "tool_images")
@patch.object(platform.Platform, "container_engine")
@patch.object(platform.Platform, "user_output")
@patch.object(platform.Platform, "__init__")
def test_Platform_install_dev_env(mock___init__: MagicMock, mock_user_input: MagicMock, 
                                  mock_container_engine: MagicMock, mock_tool_images) -> None:
    # Test setup
    mock___init__.return_value = None

    test_dev_env = MagicMock()
    test_registry_only_tool_images: list[str] = ["test_image_name1:test_image_version1", 
                                                 "test_image_name2:test_image_version2"]
    test_dev_env.get_registry_only_tool_images.return_value = test_registry_only_tool_images

    test_platform = platform.Platform()

    # Run unit under test
    test_platform.install_dev_env(test_dev_env)

    # Check expectations
    mock___init__.assert_called_once()

    test_dev_env.get_registry_only_tool_images.assert_called_once_with(mock_tool_images, False)
    mock_user_input.msg.assert_has_calls([
        call(f"\nPulling image {test_registry_only_tool_images[0]}", is_title=True),
        call(f"\nPulling image {test_registry_only_tool_images[1]}", is_title=True)
    ])
    mock_container_engine.pull.assert_has_calls([
        call(test_registry_only_tool_images[0]),
        call(test_registry_only_tool_images[1])
    ])

@patch.object(platform.Platform, "flush_descriptors")
@patch.object(platform.Platform, "container_engine")
@patch.object(platform.Platform, "user_output")
@patch.object(platform.Platform, "__init__")
def test_Platform_uninstall_dev_env_success(mock___init__: MagicMock, mock_user_output: MagicMock,
                                            mock_container_engine: MagicMock, 
                                            mock_flush_descriptors: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_platform = platform.Platform()
    mock_dev_env1 = MagicMock()
    mock_dev_env2 = MagicMock()
    mock_dev_env_to_uninstall = MagicMock()
    test_platform.local_dev_envs = [
        mock_dev_env1, mock_dev_env2, mock_dev_env_to_uninstall
    ]
    mock_dev_env1.tools = [
        {
            "image_name": "test_image_name1",
            "image_version": "test_image_version1"
        },
        {
            "image_name": "test_image_name2",
            "image_version": "test_image_version2"
        }
    ]
    mock_dev_env1.is_installed = True
    mock_dev_env2.tools = [
        {
            "image_name": "test_image_name3",
            "image_version": "test_image_version3"
        }
    ]
    mock_dev_env2.is_installed = True
    mock_dev_env_to_uninstall.tools = [
        {
            "image_name": "test_image_name1",
            "image_version": "test_image_version1"
        },
        {
            "image_name": "test_image_name3",
            "image_version": "test_image_version3"
        },
        {
            "image_name": "test_image_name4",
            "image_version": "test_image_version4"
        }
    ]
    mock_dev_env_to_uninstall.is_installed = True

    mock_container_engine.remove.return_value = True

    # Run unit under test
    test_platform.uninstall_dev_env(mock_dev_env_to_uninstall)

    # Check expectations
    mock___init__.assert_called_once()

    assert mock_dev_env_to_uninstall.is_installed == False

    mock_user_output.msg.assert_has_calls([
        call(f"\nThe tool image [bold]test_image_name1:test_image_version1[/bold] is required by another Development Environment. It won't be deleted."),
        call(f"\nThe tool image [bold]test_image_name3:test_image_version3[/bold] is required by another Development Environment. It won't be deleted."),
    ])
    mock_container_engine.remove.asssert_called_once_with("test_image_name4:test_image_version4")
    mock_flush_descriptors.assert_called_once()

@patch.object(platform.Platform, "container_engine")
@patch.object(platform.Platform, "user_output")
@patch.object(platform.Platform, "__init__")
def test_Platform_uninstall_dev_env_failure(mock___init__: MagicMock, mock_user_output: MagicMock,
                                            mock_container_engine: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_platform = platform.Platform()
    mock_dev_env1 = MagicMock()
    mock_dev_env2 = MagicMock()
    mock_dev_env_to_uninstall = MagicMock()
    test_platform.local_dev_envs = [
        mock_dev_env1, mock_dev_env2, mock_dev_env_to_uninstall
    ]
    mock_dev_env1.tools = [
        {
            "image_name": "test_image_name1",
            "image_version": "test_image_version1"
        },
        {
            "image_name": "test_image_name2",
            "image_version": "test_image_version2"
        }
    ]
    mock_dev_env1.is_installed = True
    mock_dev_env2.tools = [
        {
            "image_name": "test_image_name3",
            "image_version": "test_image_version3"
        }
    ]
    mock_dev_env2.is_installed = True
    mock_dev_env_to_uninstall.tools = [
        {
            "image_name": "test_image_name1",
            "image_version": "test_image_version1"
        },
        {
            "image_name": "test_image_name3",
            "image_version": "test_image_version3"
        },
        {
            "image_name": "test_image_name4",
            "image_version": "test_image_version4"
        }
    ]
    mock_dev_env_to_uninstall.is_installed = True

    mock_container_engine.remove.side_effect = platform.ContainerEngineError("")

    # Run unit under test
    with pytest.raises(platform.PlatformError) as exported_exception_info:
        test_platform.uninstall_dev_env(mock_dev_env_to_uninstall)

        # Check expectations
        mock___init__.assert_called_once()

        assert str(exported_exception_info) == "Platform error: Dev Env uninstall failed."
        assert mock_dev_env_to_uninstall.is_installed == True

        mock_user_output.msg.assert_has_calls([
            call(f"\nThe tool image [bold]test_image_name1:test_image_version1[/bold] is required by another Development Environment. It won't be deleted."),
            call(f"\nThe tool image [bold]test_image_name3:test_image_version3[/bold] is required by another Development Environment. It won't be deleted."),
        ])
        mock_container_engine.remove.asssert_called_once_with("test_image_name4:test_image_version4")

@patch.object(platform.Platform, "get_deserialized")
@patch.object(platform.Platform, "__init__")
def test_Platform_flush_descriptors(mock___init__: MagicMock, 
                                    mock_get_deserialized: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_platform = platform.Platform()
    test_platform.dev_env_json = MagicMock()

    mock_deserialized = MagicMock()
    mock_get_deserialized.return_value = mock_deserialized

    # Run unit under test
    test_platform.flush_descriptors()

    # Check expectations
    mock___init__.assert_called_once()

    mock_get_deserialized.assert_called_once()
    test_platform.dev_env_json.flush.assert_called_once()

    assert test_platform.dev_env_json.deserialized == mock_deserialized

@patch("dem.core.platform.os.path.exists")
@patch("dem.core.platform.os.path.isdir")
@patch.object(platform.Core, "user_output")
@patch.object(platform.Platform, "__init__")
def test_Platform_assign_dev_env(mock___init__: MagicMock, mock_user_output: MagicMock,
                                 mock_isdir: MagicMock, mock_exists: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_platform = platform.Platform()

    test_dev_env_name = "test_dev_env_name"
    test_project_path = "test_project_path"

    mock_dev_env = MagicMock()
    mock_dev_env.name = test_dev_env_name

    mock_isdir.return_value = True
    mock_exists.return_value = False

    # Run unit under test
    test_platform.assign_dev_env(mock_dev_env, test_project_path)

    # Check expectations
    mock___init__.assert_called_once()

    mock_user_output.msg.assert_called_once_with(f"\nAssigning the {test_dev_env_name} Development Environment to the project at {test_project_path}")
    mock_isdir.assert_called_once_with(f"{test_project_path}/.axem")
    mock_exists.assert_called_once_with(f"{test_project_path}/.axem/dev_env_descriptor.json")
    mock_dev_env.export.assert_called_once_with(f"{test_project_path}/.axem/dev_env_descriptor.json")

    mock_user_output.get_confirm.assert_not_called()

@patch("dem.core.platform.os.mkdir")
@patch("dem.core.platform.os.path.exists")
@patch("dem.core.platform.os.path.isdir")
@patch.object(platform.Core, "user_output")
@patch.object(platform.Platform, "__init__")
def test_Platform_assign_dev_env_missing_axem_dir(mock___init__: MagicMock, 
                                                  mock_user_output: MagicMock,
                                                  mock_isdir: MagicMock, mock_exists: MagicMock,
                                                  mock_mkdir: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_platform = platform.Platform()

    test_dev_env_name = "test_dev_env_name"
    test_project_path = "test_project_path"

    mock_dev_env = MagicMock()
    mock_dev_env.name = test_dev_env_name

    mock_isdir.return_value = False
    mock_exists.return_value = True

    # Run unit under test
    test_platform.assign_dev_env(mock_dev_env, test_project_path)

    # Check expectations
    mock___init__.assert_called_once()

    mock_user_output.msg.assert_called_once_with(f"\nAssigning the {test_dev_env_name} Development Environment to the project at {test_project_path}")
    mock_isdir.assert_called_once_with(f"{test_project_path}/.axem")
    mock_mkdir.assert_called_once_with(f"{test_project_path}/.axem")
    mock_exists.assert_called_once_with(f"{test_project_path}/.axem/dev_env_descriptor.json")
    mock_dev_env.export.assert_called_once_with(f"{test_project_path}/.axem/dev_env_descriptor.json")

@patch("dem.core.platform.os.path.exists")
@patch("dem.core.platform.os.path.isdir")
@patch.object(platform.Core, "user_output")
@patch.object(platform.Platform, "__init__")
def test_Platform_assign_dev_env_already_assigned(mock___init__: MagicMock, 
                                                  mock_user_output: MagicMock,
                                                  mock_isdir: MagicMock, mock_exists: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_platform = platform.Platform()

    test_dev_env_name = "test_dev_env_name"
    test_project_path = "test_project_path"

    mock_dev_env = MagicMock()
    mock_dev_env.name = test_dev_env_name

    mock_isdir.return_value = True
    mock_exists.return_value = True

    # Run unit under test
    test_platform.assign_dev_env(mock_dev_env, test_project_path)

    # Check expectations
    mock___init__.assert_called_once()

    mock_user_output.msg.assert_called_once_with(f"\nAssigning the {test_dev_env_name} Development Environment to the project at {test_project_path}")
    mock_isdir.assert_called_once_with(f"{test_project_path}/.axem")
    mock_exists.assert_called_once_with(f"{test_project_path}/.axem/dev_env_descriptor.json")
    mock_user_output.get_confirm.assert_called_once_with("[yellow]A Dev Env is already assigned to the project.[/]", 
                                                         "Overwrite it?")
    mock_dev_env.export.assert_called_once_with(f"{test_project_path}/.axem/dev_env_descriptor.json")