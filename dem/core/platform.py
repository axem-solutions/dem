"""Repesents the Development Platform. The platform resources can be accessed through this interface.  
"""

import os
from typing import Any
from dem.core.core import Core
from dem.core.properties import __supported_dev_env_major_version__
from dem.core.exceptions import DataStorageError, PlatformError, ContainerEngineError
from dem.core.dev_env_catalog import DevEnvCatalogs
from dem.core.data_management import LocalDevEnvJSON
from dem.core.container_engine import ContainerEngine
from dem.core.registry import Registries
from dem.core.tool_images import ToolImages
from dem.core.dev_env import DevEnv
from dem.core.hosts import Hosts

class Platform(Core):
    """ Representation of the Development Platform:
        - The available tool images.
        - The available Development Environments.
        - External resources.

        Class variables:
            _tool_images -- the available tool images
            _container_engine -- the container engine
            _regisitries -- managing the registries
            update_tool_images_on_instantiation -- can be used to disable tool update if not needed
    """
    update_tool_images_on_instantiation = True

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

    def load_dev_envs(self) -> None:
        """ Load the Development Environments from the dev_env.json file."""
        self.dev_env_json = LocalDevEnvJSON()
        self.dev_env_json.update()
        self.version = self.dev_env_json.deserialized["version"]
        self._dev_env_json_version_check(int(self.version.split('.', 1)[0]))
        self.local_dev_envs: list[DevEnv] = []
        for dev_env_descriptor in self.dev_env_json.deserialized["development_environments"]:
            self.local_dev_envs.append(DevEnv(descriptor=dev_env_descriptor))

    @property
    def tool_images(self) -> ToolImages:
        """ The tool images.

            The ToolImages() gets instantiated only at the first access.
        """
        if self._tool_images is None:
            self._tool_images = ToolImages(self.container_engine, self.registries,
                                          self.update_tool_images_on_instantiation)
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
            self._registries = Registries(self.container_engine)

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
        dev_env_to_install.check_image_availability(self.tool_images, False)

        # First check if the missing images are available in the registries.
        for tool in dev_env_to_install.tools:
            if tool["image_status"] == ToolImages.NOT_AVAILABLE:
                raise PlatformError(f"The {tool['image_name']}:{tool['image_version']} image is not available.")

        for tool in dev_env_to_install.tools:
            if tool["image_status"] == ToolImages.REGISTRY_ONLY:
                self.user_output.msg(f"\nPulling image {tool['image_name']}:{tool['image_version']}", 
                                     is_title=True)
                try:                
                    self.container_engine.pull(f"{tool['image_name']}:{tool['image_version']}")
                except ContainerEngineError as e:
                    raise PlatformError(f"Dev Env install failed. Reason: {str(e)}")

        dev_env_to_install.is_installed = True
        self.flush_descriptors()

    def uninstall_dev_env(self, dev_env_to_uninstall: DevEnv) -> None:
        """ Uninstall the Dev Env by removing the images not required anymore.

            Args:
                dev_env_to_uninstall -- the Development Environment to uninstall

            Exceptions:
                PlatformError -- if the uninstall fails
        """
        all_required_tool_images = set()
        for dev_env in self.local_dev_envs:
            if (dev_env is not dev_env_to_uninstall) and dev_env.is_installed:
                for tool in dev_env.tools:
                    all_required_tool_images.add(tool["image_name"] + ":" + tool["image_version"])

        tool_images_to_remove = set()
        for tool in dev_env_to_uninstall.tools:
            tool_image = tool["image_name"] + ":" + tool["image_version"]
            if tool_image not in all_required_tool_images:
                tool_images_to_remove.add(tool_image)

        for tool_image in tool_images_to_remove:
            try:
                self.container_engine.remove(tool_image)
            except ContainerEngineError as e:
                raise PlatformError(f"Dev Env uninstall failed. <-caused by- {str(e)}")
            
        dev_env_to_uninstall.is_installed = False
        self.flush_descriptors()

    def flush_descriptors(self) -> None:
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
        existing_dev_env = self.get_dev_env_by_name(assigned_dev_env.name)
        if existing_dev_env is not None:
            self.user_output.get_confirm("[yellow]This project is already initialized.[/]", 
                                         "Overwrite it?")
            self.local_dev_envs.remove(existing_dev_env)

        self.local_dev_envs.append(assigned_dev_env)