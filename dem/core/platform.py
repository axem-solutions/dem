"""This repesents the Development Platform. The platform resources can be access through this 
    interface.
"""
from dem.core.core import Core
from dem.core.properties import __supported_dev_env_major_version__
from dem.core.exceptions import InvalidDevEnvJson
from dem.core.dev_env_catalog import DevEnvCatalogs
from dem.core.data_management import LocalDevEnvJSON, ConfigFile
from dem.core.container_engine import ContainerEngine
from dem.core.registry import Registries
from dem.core.tool_images import ToolImages
from dem.core.dev_env import DevEnvLocal, DevEnv, DevEnv

class DevEnvSetup(Core):
    """Representation of the development setup:
        - The available tool images.
        - The available Development Environments.

    Class attributes:
        _tool_images -- the available tool images
        _container_engine -- the container engine
        _regisitries -- managing the registries
        _config_file -- contains the DEM configuration
        update_tool_images_on_instantiation -- can be used to disable tool update if not needed
    """
    _tool_images = None
    _container_engine = None
    _registries = None
    _config_file = None
    update_tool_images_on_instantiation = True

    def _dev_env_json_version_check(self) -> None:
        """Check that the dev_env.json or dev_evn_org.json file supported.

        The dev_env.json or dev_env_org.json version is stored as string in the X.Y format.
        Raises an InvalidDevEnvJson exception, if the version is not supported.
        """
        dev_env_json_major_version = int(self.version.split('.', 1)[0])
        if dev_env_json_major_version != __supported_dev_env_major_version__:
            raise InvalidDevEnvJson("The dev_env.json version v1.0 is not supported.")

    def __init__(self, dev_env_json_deserialized: dict) -> None:
        """Create a list for the Development Environments.

        Args:
            dev_env_json_deserialized -- a deserialized representation of the dev_env.json or 
                                         dev_env_org.json file
        """
        self.version = dev_env_json_deserialized["version"]
        self._dev_env_json_version_check()
        self.local_dev_envs: list[DevEnv] = []
        self._dev_env_catalogs: DevEnvCatalogs | None = None

    @classmethod
    @property
    def tool_images(cls) -> ToolImages:
        """ Only instantiate the _tool_images when first accessed, because it is time consuming.

        The decorators are needed so the tool_images can act as a class-level property, ensuring 
        only a single ToolImage class intance exists for every DevEnvSetup() instance. The class 
        variable can be accessed through a getter, so the ToolImage() gets instantiated only at the 
        first access.

        Args:
            cls - the class object
        """
        if cls._tool_images is None:
            cls._tool_images = ToolImages(cls.container_engine, cls.registries,
                                          cls.update_tool_images_on_instantiation)
        return cls._tool_images

    @classmethod
    @property
    def container_engine(cls) -> ContainerEngine:
        """ The container engine.

        The decorators are needed so the container_engine can act as a class-level property, 
        ensuring only a single ContainerEngine class intance exists for every DevEnvSetup() instance. 
        The class variable can be accessed through a getter, so the ContainerEngine() gets 
        instantiated only at the first access.

        Args:
            cls - the class object
        """
        if cls._container_engine is None:
            cls._container_engine = ContainerEngine()

        return cls._container_engine

    @classmethod
    @property
    def registries(cls) -> Registries:
        if cls._registries is None:
            cls._registries = Registries(cls.container_engine, cls.config_file)

        return cls._registries

    @classmethod
    @property
    def config_file(cls) -> ConfigFile:
        if cls._config_file is None:
            cls._config_file = ConfigFile()

        return cls._config_file

    @property
    def dev_env_catalogs(self) -> DevEnvCatalogs:
        if self._dev_env_catalogs is None:
            self._dev_env_catalogs = DevEnvCatalogs(self.config_file)

        return self._dev_env_catalogs

    def get_deserialized(self) -> dict:
        """ Create the deserialized json. """
        dev_env_json_deserialized = {}
        dev_env_json_deserialized["version"] = self.version
        dev_env_descriptors = []
        for dev_env in self.local_dev_envs:
            dev_env_descriptor = {}
            dev_env_descriptor["name"] = dev_env.name
            dev_env_descriptor["tools"] = dev_env.tools
            dev_env_descriptors.append(dev_env_descriptor)
        dev_env_json_deserialized["development_environments"] = dev_env_descriptors
        return dev_env_json_deserialized

    def get_dev_env_by_name(self, dev_env_name: str) -> ("DevEnv | DevEnvLocal | None"):
        """Get the Development Environment by name.
        
        Args:
            dev_env_name -- name of the Development Environment to get
        Returns with the instance representing the Development Environment. If the Development 
        Environment doesn't exist in the setup, the function returns with None.
        """
        for dev_env in self.local_dev_envs:
            if dev_env.name == dev_env_name:
                return dev_env

    def get_local_dev_env(self, catalog_dev_env: DevEnv) -> DevEnv | None:
        """ Check if this Development Enviroment already installed locally.

        Args:
            dev_env_setup_local -- the locally installed Development Environments
        Returns the local Dev Env object if available. None if not yet installed.
        """
        for local_dev_env in self.local_dev_envs:
            if catalog_dev_env.name == local_dev_env.name:
                return local_dev_env

class DevEnvLocalSetup(DevEnvSetup):
    """ The Local Development Platform. """
    def __init__(self) -> None:
        """ Store the local Development Environments.

        Extends the DevEnvSetup super class by populating the list of Development Environments with 
        DevEnvLocal objects.
        """
        self.json = LocalDevEnvJSON()
        super().__init__(self.json.deserialized)

        for dev_env_descriptor in self.json.deserialized["development_environments"]:
            self.local_dev_envs.append(DevEnvLocal(descriptor=dev_env_descriptor))

    def flush_to_file(self) -> None:
        """ Writes the deserialized json to the dev_env.json file."""
        # Get the up-to-date deserialized data.
        self.json.deserialized = self.get_deserialized()
        self.json.flush()

    def pull_images(self, tools: list) -> None:
        """ Pull images that are only present in the registry.
        
        Args:
            tools -- the tool images to pull (with any status, this function will filter the 
                     registry only ones)
        """

        # Remove the duplications and the locally already available tools
        tool_images_to_pull = set()
        for tool in tools:
            tool_image = tool["image_name" ] + ':' + tool["image_version"]
            if (tool["image_status"] == ToolImages.REGISTRY_ONLY):
                tool_images_to_pull.add(tool_image)

        for tool_image in tool_images_to_pull:
            self.user_output.msg("\nPulling image "+ tool_image, is_title=True)
            self.container_engine.pull(tool_image)

    def run_container(self, tool_image: str, workspace_path: str, command: str, privileged: bool) -> None:
        """ Run the tool image.

        Args:
            tool_image -- tool image to run
            workspace_path -- workspace path
            command -- command to be passed to the assigned tool image
            priviliged -- give extended priviliges to the container
        """
        self.container_engine.run(tool_image, workspace_path, command, privileged)
