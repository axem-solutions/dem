"""Repesents the Development Platform. The platform resources can be accessed through this interface.  
"""

import os, truststore
from typing import Any, Generator
from dem.core.core import Core
from dem.core.properties import __supported_dev_env_major_version__
from dem.core.exceptions import DataStorageError, PlatformError, ContainerEngineError
from dem.core.dev_env_catalog import DevEnvCatalogs
from dem.core.data_management import LocalDevEnvJSON
from dem.core.container_engine import ContainerEngine
from dem.core.registry import Registries
from dem.core.tool_images import ToolImages, ToolImage
from dem.core.dev_env import DevEnv
from dem.core.hosts import Hosts

class Platform(Core):
    """ Representation of the Development Platform:
        - The available tool images.
        - The available Development Environments.
        - External resources.
    """

    def _dev_env_json_version_check(self, dev_env_json_major_version: int) -> None:
        """ Check that the json file is supported.

            The version is stored as a string in the X.Y format.
            Raises an DataStorageError exception, if the version is not supported.
        """
        
        if dev_env_json_major_version != __supported_dev_env_major_version__:
            raise DataStorageError("The dev_env.json version v1.0 is not supported.")

    def __init__(self) -> None:
        """ Init the class."""
        self._dev_env_catalogs: DevEnvCatalogs | None = None
        self._tool_images = None
        self._container_engine = None
        self._registries = None
        self._hosts = None
        self.default_dev_env_name: str = ""
        self.local_dev_envs: list[DevEnv] = []
        self.are_tool_images_assigned: bool = False

        # Set this to true in the platform instance to get the tool image info from the registries
        self.get_tool_image_info_from_registries = False

    def configure(self) -> None:
        """ Configure the Development Platform."""
        if self.config_file.use_native_system_cert_store:
            truststore.inject_into_ssl()

    def load_dev_envs(self) -> None:
        """ Load the Development Environments from the dev_env.json file.
        
            The Dev Envs will only contain the descriptors and not the ToolImage instances.
        """
        self.dev_env_json = LocalDevEnvJSON()
        self.dev_env_json.update()
        self.version = self.dev_env_json.deserialized["version"]
        self._dev_env_json_version_check(int(self.version.split('.', 1)[0]))
        self.default_dev_env_name = self.dev_env_json.deserialized.get("default_dev_env", "")
        for dev_env_descriptor in self.dev_env_json.deserialized["development_environments"]:
            self.local_dev_envs.append(DevEnv(descriptor=dev_env_descriptor))

    def assign_tool_image_instances_to_all_dev_envs(self) -> None:
        """ Assign the ToolImage instances to all Development Environments."""
        for dev_env in self.local_dev_envs:
            dev_env.assign_tool_image_instances(self.tool_images)
        self.are_tool_images_assigned = True

    @property
    def tool_images(self) -> ToolImages:
        """ The tool images.

            The ToolImages() gets instantiated only at the first access.
        """
        if self._tool_images is None:
            self._tool_images = ToolImages(self.container_engine, self.registries)
            self._tool_images.update(True, self.get_tool_image_info_from_registries)
        return self._tool_images
    
    @property
    def container_engine(self) -> ContainerEngine:
        """ The container engine.

            The ContainerEngine() gets instantiated only at the first access.
        """
        if self._container_engine is None:
            self._container_engine = ContainerEngine()

        return self._container_engine

    @property
    def registries(self) -> Registries:
        """ The registries.

            The Registries() gets instantiated only at the first access.
        """
        if self._registries is None:
            self._registries = Registries()

        return self._registries

    @property
    def dev_env_catalogs(self) -> DevEnvCatalogs:
        """ The Development Environment Catalogs.

            The DevEnvCatalogs() gets instantiated only at the first access.
        """
        if self._dev_env_catalogs is None:
            self._dev_env_catalogs = DevEnvCatalogs()

        return self._dev_env_catalogs

    @property
    def hosts(self) -> Hosts:
        """ The hosts.
        
            The Hosts() gets instantiated only at the first access.
        """
        if self._hosts is None:
            self._hosts = Hosts()

        return self._hosts

    def get_deserialized(self) -> dict:
            """ Create the deserialized json. 
            
                Return the dev_env.json as a dict.
            """
            dev_env_json_deserialized: dict[str, Any] = {
                "version": self.version,
                "default_dev_env": self.default_dev_env_name,
                "development_environments": [
                    dev_env.get_deserialized()
                    for dev_env in self.local_dev_envs
                ]
            }
            return dev_env_json_deserialized

    def get_dev_env_by_name(self, dev_env_name: str) -> DevEnv | None:
        """ Get the Development Environment by name.
        
            Args:
                dev_env_name -- name of the Development Environment to get

            Return with the instance representing the Development Environment. If the Development 
            Environment doesn't exist in the setup, return with None.
        """
        for dev_env in self.local_dev_envs:
            if dev_env.name == dev_env_name:
                return dev_env

    def install_dev_env(self, dev_env_to_install: DevEnv) -> None:
        """ Install the Dev Env by pulling the required images.
        
            Args:
                dev_env_to_install -- the Development Environment to install
        """
        for tool_image in dev_env_to_install.tool_images:
            if tool_image.availability is ToolImage.REGISTRY_ONLY or \
               tool_image.availability is ToolImage.NOT_AVAILABLE:
                self.user_output.msg(f"\nPulling image {tool_image.name}", is_title=True)
                try:                
                    self.container_engine.pull(tool_image.name)
                except ContainerEngineError as e:
                    raise PlatformError(f"Dev Env install failed. --> {str(e)}")

        dev_env_to_install.is_installed = True
        self.flush_dev_env_properties()

    def uninstall_dev_env(self, dev_env_to_uninstall: DevEnv) -> Generator:
        """ Uninstall the Dev Env by removing the images not required anymore.

            Args:
                dev_env_to_uninstall -- the Development Environment to uninstall

            Returns:
                Generator -- the status messages

            Raises:
                PlatformError -- if the uninstall fails
        """
        if not self.are_tool_images_assigned:
            self.assign_tool_image_instances_to_all_dev_envs()

        all_required_tool_images = set()
        for dev_env in self.local_dev_envs:
            if (dev_env is not dev_env_to_uninstall) and dev_env.is_installed:
                for tool_image in dev_env.tool_images:
                    all_required_tool_images.add(tool_image.name)

        tool_images_to_remove = set()
        for tool_image in dev_env_to_uninstall.tool_images:
            if tool_image.availability == ToolImage.NOT_AVAILABLE or tool_image.availability == ToolImage.REGISTRY_ONLY:
                yield f"[yellow]Warning: The {tool_image.name} image could not be removed, because it is not available locally.[/]"
                continue

            if tool_image.name not in all_required_tool_images:
                tool_images_to_remove.add(tool_image.name)

        for tool_image_name in tool_images_to_remove:
            try:
                self.container_engine.remove(tool_image_name)
            except ContainerEngineError as e:
                raise PlatformError(f"Dev Env uninstall failed. --> {str(e)}")
            else:
                yield f"The {tool_image_name} image has been removed."
            
        dev_env_to_uninstall.is_installed = False
        if self.default_dev_env_name == dev_env_to_uninstall.name:
            self.default_dev_env_name = ""
        self.flush_dev_env_properties()

    def flush_dev_env_properties(self) -> None:
        """ Writes the deserialized json to the dev_env.json file."""
        # Get the up-to-date deserialized data.
        self.dev_env_json.deserialized = self.get_deserialized()
        self.dev_env_json.flush()

    def assign_dev_env(self, dev_env_to_assign: DevEnv, project_path: str) -> None:
        """ Assign the Development Environment to the project, by exporting the Dev Env's desriptor
            to the project's .axem directory.
        
            Args:
                dev_env_to_assign -- the Development Environment to assign
                project_path -- the path of the project
        """
        self.user_output.msg(f"\nAssigning the {dev_env_to_assign.name} Development Environment to the project at {project_path}")

        path: str = f"{project_path}/.axem"
        if not os.path.isdir(path):
            os.mkdir(path)

        path = f"{path}/dev_env_descriptor.json"
        if os.path.exists(path):
            self.user_output.get_confirm("[yellow]A Dev Env is already assigned to the project.[/]", 
                                         "Overwrite it?")

        dev_env_to_assign.export(path)

    def init_project(self, project_path: str) -> None:
        """ Init the project by saving the Dev Env's descriptor to the local Dev Env storage.

            Args:
                assigned_dev_env -- the Development Environment assigned to the project
        """
        descriptor_path = f"{project_path}/.axem/dev_env_descriptor.json"
        if not os.path.exists(descriptor_path):
            raise FileNotFoundError(f"The {descriptor_path} file does not exist.")

        assigned_dev_env = DevEnv(descriptor_path=descriptor_path)
        assigned_dev_env.assign_tool_image_instances(self.tool_images)
        existing_dev_env = self.get_dev_env_by_name(assigned_dev_env.name)
        if existing_dev_env is not None:
            self.user_output.get_confirm("[yellow]This project is already initialized.[/]", 
                                         "Overwrite it?")
            self.local_dev_envs.remove(existing_dev_env)

        self.local_dev_envs.append(assigned_dev_env)