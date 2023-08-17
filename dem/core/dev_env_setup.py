"""This module represents the Development Environments."""
# dem/core/dev_env_setup.py

from dem.core.core import Core
from dem.core.exceptions import InvalidDevEnvJson
from dem.core.properties import __supported_dev_env_major_version__
from dem.core.tool_images import ToolImages
from dem.core.data_management import LocalDevEnvJSON, OrgDevEnvJSON, ConfigFile
from dem.core.container_engine import ContainerEngine
from dem.core.registry import Registries

class DevEnv(Core):
    """ A Development Environment."""
    supported_tool_types = ( 
        "build system",
        "toolchain",
        "debugger",
        "deployer",
        "test framework",
        "CI/CD server",
    )

    def _check_tool_type_support(self, descriptor: dict) -> None:
        """ Check that the Dev Env doesn't contain an unsupported tool type.
        
            Private function that gets called on instantiation.
            Args:
                descriptor -- the description of the Development Environment from the dev_env.json 
                              file
        """
        for tool in descriptor["tools"]:
            if tool["type"] not in self.supported_tool_types:
                raise InvalidDevEnvJson("The following tool type is not supported: " + tool["type"])

    def __init__(self, descriptor: dict) -> None:
        """ Init the DevEnv class.
        
            Args:
                descriptor -- the description of the Development Environment from the dev_env.json 
                              file
        """
        self._check_tool_type_support(descriptor)
        self.name = descriptor["name"]
        self.tools = descriptor["tools"]

    def check_image_availability(self, tool_images: ToolImages, update_tool_images: bool = False,
                                 local_only: bool = False) -> list:
        """ Checks the tool image's availability.
        
            Updates the "image_status" key for the tool dictionary.
            Returns with the statuses of the Dev Env tool images.

            Args:
                tool_images -- the images the Dev Envs can access
                update_tool_images -- update the list of available tool images
                local_only -- only local images are used
        """
        if update_tool_images == True:
            tool_images.local.update()
            if local_only is False:
                tool_images.registry.update()

        local_tool_images = tool_images.local.elements

        if local_only is True:
            registry_tool_images = []
        else:
            registry_tool_images = tool_images.registry.elements

        image_statuses = []
        for tool in self.tools:
            tool_image_name = tool["image_name"] + ':' + tool["image_version"]
            if (tool_image_name in local_tool_images) and (tool_image_name in registry_tool_images):
                image_status = ToolImages.LOCAL_AND_REGISTRY
            elif (tool_image_name in local_tool_images):
                image_status = ToolImages.LOCAL_ONLY
            elif (tool_image_name in registry_tool_images):
                image_status = ToolImages.REGISTRY_ONLY
            else:
                image_status = ToolImages.NOT_AVAILABLE
            image_statuses.append(image_status)
            tool["image_status"] = image_status

        return image_statuses

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
        self.dev_envs = []

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

    def get_deserialized(self) -> dict:
        """ Create the deserialized json. """
        dev_env_json_deserialized = {}
        dev_env_json_deserialized["version"] = self.version
        dev_env_descriptors = []
        for dev_env in self.dev_envs:
            dev_env_descriptor = {}
            dev_env_descriptor["name"] = dev_env.name
            dev_env_descriptor["tools"] = dev_env.tools
            dev_env_descriptors.append(dev_env_descriptor)
        dev_env_json_deserialized["development_environments"] = dev_env_descriptors
        return dev_env_json_deserialized

    def get_dev_env_by_name(self, dev_env_name: str) -> ("DevEnvOrg | DevEnvLocal | None"):
        """Get the Development Environment by name.
        
        Args:
            dev_env_name -- name of the Development Environment to get
        Returns with the instance representing the Development Environment. If the Development 
        Environment doesn't exist in the setup, the function returns with None.
        """
        for dev_env in self.dev_envs:
            if dev_env.name == dev_env_name:
                return dev_env

class DevEnvLocal(DevEnv):
    """ Local Development Environment """
    def __init__(self, descriptor: dict | None = None, dev_env_org: "DevEnvOrg | None" = None):
        """Init a local DevEnv class

        The class can be initialized either based on the Dev Env descriptor from the dev_env.json 
        file or on an already existing DevEnvOrg object.
        Args:
            dev_env_json_deserialized -- a deserialized representation of the dev_env.json file
            dev_env_org -- the DevEnvOrg object to make a copy from (note: forward reference)
        """
        if descriptor is not None:
            super().__init__(descriptor)
        else:
            self.name = dev_env_org.name
            self.tools = dev_env_org.tools

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
            self.dev_envs.append(DevEnvLocal(descriptor=dev_env_descriptor))

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

class DevEnvOrg(DevEnv):
    """ A Development Environment available for the organization."""
    def get_local_instance(self, dev_env_setup_local: DevEnvLocalSetup) -> (DevEnvLocal | None):
        """ Check if this Development Enviroment already installed locally.

        Args:
            dev_env_setup_local -- the locally installed Development Environments
        Returns the local Dev Env object if available. None if not yet installed.
        """
        for dev_env_local in dev_env_setup_local.dev_envs:
            if self.name == dev_env_local.name:
                return dev_env_local

class DevEnvOrgSetup(DevEnvSetup):
    """ The organization's development setup. The user can install Dev Envs listed in this class.

    Class attributes:
        json -- deserialized json representing the organization's setup 
    """
    json = OrgDevEnvJSON()

    def __init__(self) -> None:
        """Store the Development Environments available for the organization.

        Extends the DevEnvSetup super class by populating the list of Development Environments with 
        DevEnvOrg objects.
        """
        super().__init__(self.json.read())

        for dev_env_descriptor in self.json.deserialized["development_environments"]:
            self.dev_envs.append(DevEnvOrg(descriptor=dev_env_descriptor))
