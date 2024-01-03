"""Repesents the Development Platform. The platform resources can be accessed through this interface.  
"""
from dem.core.core import Core
from dem.core.properties import __supported_dev_env_major_version__
from dem.core.exceptions import InvalidDevEnvJson, PlatformError, ContainerEngineError
from dem.core.dev_env_catalog import DevEnvCatalogs
from dem.core.data_management import LocalDevEnvJSON, ConfigFile
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
            _config_file -- contains the DEM configuration
            update_tool_images_on_instantiation -- can be used to disable tool update if not needed
    """
    update_tool_images_on_instantiation = True

    def _dev_env_json_version_check(self) -> None:
        """ Check that the json file is supported.

            The version is stored as string in the X.Y format.
            Raises an InvalidDevEnvJson exception, if the version is not supported.
        """
        dev_env_json_major_version = int(self.version.split('.', 1)[0])
        if dev_env_json_major_version != __supported_dev_env_major_version__:
            raise InvalidDevEnvJson("The dev_env.json version v1.0 is not supported.")

    def __init__(self) -> None:
        """ Init the class, by creating a list of the Development Environments."""

        self.dev_env_json = LocalDevEnvJSON()
        self.version: str = self.dev_env_json.deserialized["version"]
        self._dev_env_json_version_check()
        self._dev_env_catalogs = None
        self._tool_images = None
        self._container_engine = None
        self._registries = None
        self._config_file = None
        self._hosts = None

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
            self._registries = Registries(self.container_engine, self.config_file)

        return self._registries

    @property
    def config_file(self) -> ConfigFile:
        """ The config file.

            The ConfigFile() gets instantiated only at the first access.
        """
        if self._config_file is None:
            self._config_file = ConfigFile()

        return self._config_file

    @property
    def dev_env_catalogs(self) -> DevEnvCatalogs:
        """ The Development Environment Catalogs.

            The DevEnvCatalogs() gets instantiated only at the first access.
        """
        if self._dev_env_catalogs is None:
            self._dev_env_catalogs = DevEnvCatalogs(self.config_file)

        return self._dev_env_catalogs

    @property
    def hosts(self) -> Hosts:
        """ The hosts.
        
            The Hosts() gets instantiated only at the first access.
        """
        if self._hosts is None:
            self._hosts = Hosts(self.config_file)

        return self._hosts

    def get_deserialized(self) -> dict:
            """ Create the deserialized json. 
            
                Return the dev_env.json as a dict.
            """
            dev_env_json_deserialized = {
                "version": self.version,
                "development_environments": [
                    {
                        "name": dev_env.name,
                        "installed": dev_env.is_installed,
                        "tools": dev_env.tools
                    }
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
        for tool_image in dev_env_to_install.get_registry_only_tool_images(self.tool_images, False):
            self.user_output.msg(f"\nPulling image {tool_image}", is_title=True)
            self.container_engine.pull(tool_image)

    def uninstall_dev_env(self, dev_env_to_uninstall: DevEnv) -> None:
        """ Uninstall the Dev Env by removing the images not required anymore.

            Exceptions:
                PlatformError -- if the uninstall fails
        
            Args:
                dev_env_to_uninstall -- the Development Environment to uninstall
        """
        all_required_tool_images = set()
        for dev_env in self.local_dev_envs:
            if (dev_env is not dev_env_to_uninstall) and (dev_env.is_installed == "True"):
                for tool in dev_env.tools:
                    all_required_tool_images.add(tool["image_name"] + ":" + tool["image_version"])

        for tool in dev_env_to_uninstall.tools:
            tool_image = tool["image_name"] + ":" + tool["image_version"]
            if tool_image in all_required_tool_images:
                self.user_output.msg(f"\nThe tool image [bold]{tool_image}[/bold] is required by another Development Environment. It won't be deleted.")
            else:
                try:
                    self.container_engine.remove(tool_image)
                except ContainerEngineError:
                    raise PlatformError("Dev Env uninstall failed.")
            
        dev_env_to_uninstall.is_installed = "False"
        self.flush_descriptors()

    def flush_descriptors(self) -> None:
        """ Writes the deserialized json to the dev_env.json file."""
        # Get the up-to-date deserialized data.
        self.dev_env_json.deserialized = self.get_deserialized()
        self.dev_env_json.flush()
