"""This module represents the Development Environments."""
# dem/core/dev_env_setup.py

from dem.core.exceptions import InvalidDevEnvJson
from dem.core.properties import __supported_dev_env_major_version__

(
    IMAGE_LOCAL_ONLY,
    IMAGE_REGISTRY_ONLY,
    IMAGE_LOCAL_AND_REGISTRY,
    IMAGE_NOT_AVAILABLE,
) = range(4)

class DevEnv:
    """A Development Environment.
    
    Args:
        descriptor -- the description of the Development Environment from the dev_env.json file
    """
    supported_tool_types = ( 
        "build system",
        "toolchain",
        "debugger",
        "deployer",
        "test framework",
    )

    def _check_tool_type_support(self, descriptor: dict):
        """ Check that the Dev Env doesn't contain an unsupported tool type.
        
            Private function that gets called on instantiation.
            Args:
                descriptor -- the description of the Development Environment from the dev_env.json 
                              file
        """
        for tool in descriptor["tools"]:
            if tool["type"] not in self.supported_tool_types:
                raise InvalidDevEnvJson("The following tool type is not supported: " + tool["type"])

    def __init__(self, descriptor: dict | None = None, dev_env_org: "DevEnvOrg | None" = None):
        """ Init the DevEnv class.
        
            Args:
                descriptor -- the description of the Development Environment from the dev_env.json 
                              file
                dev_env_org -- set when creating a copy (note: forward reference)
        """
        if isinstance(descriptor, dict):
            self._check_tool_type_support(descriptor)
            self.name = descriptor["name"]
            self.tools = descriptor["tools"]
        else:
            self.name = dev_env_org.name
            self.tools = dev_env_org.tools

    def check_image_availability(self, local_images: list, registry_images: list) -> list:
        """ Checks the tool image's availability.
        
            Updates the "image_status" key for the tool dictionary.
            Args:
                local_images -- list of the local image names with tags
                registry_images -- list of the images available in the registry (name + tag)
            Returns with the statuses of the Dev Env tool images.
        """
        image_statuses = []
        for tool in self.tools:
            image_status = IMAGE_NOT_AVAILABLE
            tool_image = tool["image_name"] + ':' + tool["image_version"]
            if tool_image in local_images:
                image_status = IMAGE_LOCAL_ONLY
            if tool_image in registry_images:
                if image_status == IMAGE_LOCAL_ONLY:
                    image_status = IMAGE_LOCAL_AND_REGISTRY
                else:
                    image_status = IMAGE_REGISTRY_ONLY
            image_statuses.append(image_status)
            tool["image_status"] = image_status
        return image_statuses

class DevEnvSetup:
    """Group of the Development Environments.

    Args:
        dev_env_json_deserialized -- a deserialized representation of the dev_env.json or 
                                     dev_env_org.json file
    """
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

    def get_deserialized(self) -> dict:
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


class DevEnvLocal(DevEnv):
    """Local Development Environment

    Same as the DevEnv super class.
    """
    def __init__(self, descriptor: dict | None = None, dev_env_org: "DevEnvOrg | None" = None):
        """Init a local DevEnv class

        The class is initialized either based on the Dev Env descriptor from the dev_env.json file 
        or on a DevEnvOrg class.
        Args:
            dev_env_json_deserialized -- a deserialized representation of the dev_env.json file
            dev_env_org -- the DevEnvOrg object to make a copy from (note: forward reference)
        """
        super().__init__(descriptor, dev_env_org)

class DevEnvLocalSetup(DevEnvSetup):
    def __init__(self, dev_env_json_deserialized: dict):
        """Store the local Development Environments.

        Extends the DevEnvSetup super class by populating the list of Development Environments with 
        DevEnvLocal objects.
        Args:
            dev_env_json_deserialized -- a deserialized representation of the dev_env.json file
        """
        super().__init__(dev_env_json_deserialized)

        for dev_env_descriptor in dev_env_json_deserialized["development_environments"]:
            self.dev_envs.append(DevEnvLocal(descriptor=dev_env_descriptor))

class DevEnvOrg(DevEnv):
    """A Development Environment available for the organization."""
    def get_local_instance(self, dev_env_setup_local: DevEnvLocalSetup) -> (DevEnvLocal | None):
        """Check if this Development Enviroment already installed locally.

        Args:
            dev_env_setup_local -- the locally installed Development Environments
        Returns the local Dev Env object if available. None if not yet installed.
        """
        for dev_env_local in dev_env_setup_local.dev_envs:
            if self.name == dev_env_local.name:
                return dev_env_local

class DevEnvOrgSetup(DevEnvSetup):
    def __init__(self, dev_env_json_deserialized: dict) -> None:
        """Store the Development Environments available for the organization.

        Extends the DevEnvSetup super class by populating the list of Development Environments with 
        DevEnvOrg objects.
        Args:
            dev_env_json_deserialized -- a deserialized representation of the dev_env_org.json file
        """
        super().__init__(dev_env_json_deserialized)

        for dev_env_descriptor in dev_env_json_deserialized["development_environments"]:
            self.dev_envs.append(DevEnvOrg(descriptor=dev_env_descriptor))
    
    def get_dev_env(self, dev_env_name: str) -> (DevEnvOrg | None):
        """Get the Development Environment fromt thr organization setup by name.
        
        Args:
            dev_env_name -- name of the Development Environment to get
        Returns with the DevEnvOrg instance representing the Development Environment. If the 
        Development Environment doesn't exist in the organization, the function returns with None.
        """
        for dev_env in self.dev_envs:
            if dev_env.name == dev_env_name:
                return dev_env