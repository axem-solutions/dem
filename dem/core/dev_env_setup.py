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
        descriptor (dict): The description of the Development Environment from 
            the dev_env.json file.
    """
    supported_tool_types = ( 
        "build system",
        "toolchain",
        "debugger",
        "deployer",
        "test framework",
    )

    def _check_tool_type_support(self, descriptor: dict):
        for tool in descriptor["tools"]:
            if tool["type"] not in self.supported_tool_types:
                raise InvalidDevEnvJson("The following tool type is not supported: " + tool["type"])

    def __init__(self, descriptor: dict):
        self._check_tool_type_support(descriptor)
        self.name = descriptor["name"]
        self.tools = descriptor["tools"]

    def check_image_availability(self, local_images: list, registry_images: list) -> list:
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
    """The Development Environment setup. Contains all the Development Environments
        available on this computer
        
    Args:
        dev_env_json_deserialized (dict): A deserialized representation of the 
            dev_env.json file.
    """
    def dev_env_json_version_check(self):
        dev_env_json_major_version = int(self.version.split('.', 1)[0])
        if dev_env_json_major_version != __supported_dev_env_major_version__:
            raise InvalidDevEnvJson("The dev_env.json version v1.0 is not supported.")

    def __init__(self, dev_env_json_deserialized: dict):
        self.version = dev_env_json_deserialized["version"]
        self.dev_env_json_version_check()
        self.dev_envs = []

class DevEnvLocal(DevEnv):
    pass

class DevEnvLocalSetup(DevEnvSetup):
    def __init__(self, dev_env_json_deserialized: dict):
        super().__init__(dev_env_json_deserialized)

        for dev_env_descriptor in dev_env_json_deserialized["development_environments"]:
            self.dev_envs.append(DevEnvLocal(dev_env_descriptor))

class DevEnvOrg(DevEnv):
    def is_installed_locally(self, dev_env_setup_local: DevEnvLocalSetup):
        for dev_env_local in dev_env_setup_local.dev_envs:
            if self.name == dev_env_local.name:
                return True
        return False


class DevEnvOrgSetup(DevEnvSetup):
    def dev_env_json_version_check(self):
        return super().dev_env_json_version_check()

    def __init__(self, dev_env_json_deserialized: dict):
        super().__init__(dev_env_json_deserialized)

        for dev_env_descriptor in dev_env_json_deserialized["development_environments"]:
            self.dev_envs.append(DevEnvOrg(dev_env_descriptor))