"""Repesents the Development Platform. The platform resources can be accessed through this interface.  
"""

import os, truststore
from typing import Any, Generator
from dem.core.core import Core
from dem.core.properties import __supported_dev_env_major_version__
from dem.core.exceptions import DataStorageError, PlatformError, ContainerEngineError, DevEnvError
from dem.core.dev_env_catalog import DevEnvCatalogs
from dem.core.data_management import LocalDevEnvJSON
from dem.core.registry import Registries
from dem.core.tool_images import ToolImages, ToolImage
from dem.core.dev_env import DevEnv
from dem.core.hosts import Hosts
from dem.core.api_server import APIServer
from fastapi import FastAPI

class Platform(Core):
    """ Representation of the Development Platform:
        - The available tool images.
        - The available Development Environments.
        - The available registries.
        - The available hosts.
        - External resources.

        The Development Platform is a singleton class. The instance can be accessed through the
        platform variable.

        Attributes:
            fastapi_app -- the FastAPI application
    """
    fastapi_app = FastAPI()

    def _dev_env_json_version_check(self, dev_env_json_major_version: int) -> None:
        """ Check that the json file is supported.

            The version is stored as a string in the X.Y format.
            Raises an DataStorageError exception, if the version is not supported.

            Args:
                dev_env_json_major_version -- the major version of the dev_env.json file

            Raises:
                DataStorageError -- if the version is not supported
        """
        
        if dev_env_json_major_version != __supported_dev_env_major_version__:
            raise DataStorageError("The dev_env.json version v1.0 is not supported.")

    def __init__(self) -> None:
        """ Init the class."""
        self._dev_env_catalogs: DevEnvCatalogs | None = None
        self._tool_images = None
        self._container_engine = None
        self._registries = None

        # Load the configuration file
        self.config_file.update()

        self.hosts: Hosts = Hosts()
        self.default_dev_env_name: str = ""
        self.local_dev_envs: list[DevEnv] = []
        self.are_tool_images_assigned: bool = False
        self.api_server = APIServer(self.fastapi_app)

        # Set this to true in the platform instance to get the tool image info from the registries
        self.get_tool_image_info_from_registries = False

    def configure(self) -> None:
        """ Configure the Development Platform."""
        if self.config_file.use_native_system_cert_store:
            truststore.inject_into_ssl()

    def load_dev_envs(self) -> None:
        """ Load the Development Environments from the dev_env.json file.
        
            After this method the Dev Envs will only contain the descriptors and not the ToolImage instances.
        """
        self.dev_env_json = LocalDevEnvJSON()
        self.dev_env_json.update()
        self.version = self.dev_env_json.deserialized["version"]
        self._dev_env_json_version_check(int(self.version.split('.', 1)[0]))
        self.default_dev_env_name = self.dev_env_json.deserialized.get("default_dev_env", "")
        for dev_env_descriptor in self.dev_env_json.deserialized["development_environments"]:
            self.local_dev_envs.append(DevEnv(dev_env_descriptor, self.hosts))

    def assign_tool_image_instances_to_all_dev_envs(self) -> None:
        """ Assign the ToolImage instances to all Development Environments."""
        failed_dev_envs: str = []
        for dev_env in self.local_dev_envs:
            try:
                dev_env.start_engines()
                dev_env.assign_tool_image_instances(self.tool_images)
            except DevEnvError as e:
                failed_dev_envs.append(dev_env.name)
                self.user_output.msg(f"[red]Error: {e}[/]")
        self.are_tool_images_assigned = True

        if failed_dev_envs:
            self.user_output.msg(f"[red]Error: Failed to assign Tool Images to the following Development Environments: {failed_dev_envs}[/]")

    @property
    def tool_images(self) -> ToolImages:
        """ The tool images.

            The ToolImages() gets instantiated only at the first access.
        """
        if self._tool_images is None:
            self._tool_images = ToolImages(self.hosts.local.container_engine, self.registries)
            self._tool_images.update(True, self.get_tool_image_info_from_registries)
        return self._tool_images
    
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

            Raises:
                PlatformError -- if the install fails
        """
        for task in dev_env_to_install.tasks:
            tool_image_name: str = task.image
            try:
                tool_image = dev_env_to_install.assigned_tool_images[tool_image_name]
            except KeyError:
                raise PlatformError(f"The {tool_image_name} Tool Image is not assigned to the Development Environment.")

            host = self.hosts.get_host_by_name(task.host_name)
            if host is None:
                raise PlatformError(f"The {task.host_name} host is not available.")

            self.user_output.msg(f"\nPulling image {tool_image.name}", is_title=True)
            try:                
                host.container_engine.pull(tool_image_name)
            except ContainerEngineError as e:
                raise PlatformError(f"Dev Env install failed. --> {str(e)}")

        if dev_env_to_install.enable_docker_network:
            self.hosts.local.container_engine.create_network(dev_env_to_install.name)

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

        all_required_tool_images: dict[str, set] = {}

        for dev_env in self.local_dev_envs:
            if dev_env is dev_env_to_uninstall or not dev_env.is_installed:
                continue
            for task in dev_env.tasks:
                required_tool_images_per_host: set = all_required_tool_images.get(task.host.name, set())
                required_tool_images_per_host.add(task.image)
                all_required_tool_images[task.host.name] = required_tool_images_per_host

        for task in dev_env_to_uninstall.tasks:
            if task.host.name in all_required_tool_images.keys() and \
                task.image in all_required_tool_images[task.host.name]:
                continue

            try:
                task.host.container_engine.remove(task.image)
            except ContainerEngineError as e:
                raise PlatformError(f"Dev Env uninstall failed. --> {str(e)}")
            else:
                yield f"The {task.image} image has been removed."

        if dev_env_to_uninstall.enable_docker_network:
            self.hosts.local.container_engine.remove_network(dev_env_to_uninstall.name)
            
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

        assigned_dev_env = DevEnv.from_descriptor_path(descriptor_path)
        assigned_dev_env.assign_tool_image_instances(self.tool_images)
        existing_dev_env = self.get_dev_env_by_name(assigned_dev_env.name)
        if existing_dev_env is not None:
            self.user_output.get_confirm("[yellow]This project is already initialized.[/]", 
                                         "Overwrite it?")
            self.local_dev_envs.remove(existing_dev_env)

        self.local_dev_envs.append(assigned_dev_env)