"""This module represents the Development Environments."""
# dem/core/dev_env_setup.py

from dem.core.exceptions import InvalidDevEnvJson
from dem.core.properties import __supported_dev_env_major_version__

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

    def validate(self, local_images: list):
        for tool in self.tools:
            tool_image = tool["image_name"] + ':' + tool["image_version"]
            if tool_image in local_images:
                tool["is_image_available"] = True
            else:
                tool["is_image_available"] = False

class DevEnvSetup:
    """The Development Environment setup. Contains all the Development Environments
        available on this computer
        
    Args:
        dev_env_json_deserialized (dict): A deserialized representation of the 
            dev_env.json file.
    """
    def __dev_env_json_version_check(self):
        dev_env_json_major_version = int(self.version.split('.', 1)[0])
        if dev_env_json_major_version != __supported_dev_env_major_version__:
            raise InvalidDevEnvJson("The dev_env.json version v1.0 is not supported.")

    def __init__(self, dev_env_json_deserialized: dict):
        self.version = dev_env_json_deserialized["version"]
        self.__dev_env_json_version_check()

        self.dev_envs = []
        for dev_env_descriptor in dev_env_json_deserialized["development_environments"]:
            self.dev_envs.append(DevEnv(dev_env_descriptor))