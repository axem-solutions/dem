"""This module represents a Development Environment."""
# dem/core/dev_env.py

from dem.core.core import Core
from dem.core.tool_images import ToolImages
import json, os

class DevEnv(Core):
    """ A Development Environment.
        
        Class variables:
            supported_tool_types -- supported tool types
    """ 
    supported_tool_types = ( 
        "build system",
        "toolchain",
        "debugger",
        "deployer",
        "test framework",
        "CI/CD server",
    )

    def __init__(self, descriptor: dict | None = None, 
                 dev_env_to_copy: "DevEnv | None" = None, 
                 descriptor_path: str | None = None) -> None:
        """ Init the DevEnv class. 
        
            A new instance can be created:
            - from a Dev Env descriptor
            - based on another Dev Env
            - from a descriptor avaialable at the given path.

            Only one of the arguments can be used at a time.
        
            Args:
                descriptor -- the description of the Development Environment from the dev_env.json 
                              file
                dev_env_to_copy -- the DevEnv instance to copy
                descriptor_path -- the path of the descriptor file

            Exceptions:
                ValueError -- if more than one of the arguments is not None
        """

        # Only one of the arguments can be not None
        if sum(arg is not None for arg in [descriptor, dev_env_to_copy, descriptor_path]) > 1:
            raise ValueError("Only one of the arguments can be not None.")

        if descriptor_path:
            if not os.path.exists(descriptor_path):
                raise FileNotFoundError("dev_env_descriptor.json doesn't exist.")
            with open(descriptor_path, "r") as file:
                descriptor = json.load(file)

        if descriptor:
            self.name: str = descriptor["name"]
            self.tools: str = descriptor["tools"]
            descriptor_installed = descriptor.get("installed", "False")
            if "True" == descriptor_installed:
                self.is_installed = True
            else:
                self.is_installed = False
        else:
            self.name = dev_env_to_copy.name
            self.tools = dev_env_to_copy.tools

    def check_image_availability(self, all_tool_images: ToolImages, 
                                 update_tool_image_store: bool = False,
                                 local_only: bool = False) -> list:
        """ Checks the tool image's availability.
        
            Updates the "image_status" key for the tool dictionary.
            Returns with the statuses of the Dev Env tool images.

            Args:
                all_tool_images -- the images the Dev Envs can access
                update_tool_images -- update the list of available tool images
                local_only -- only local images are used
        """
        if update_tool_image_store == True:
            all_tool_images.local.update()
            if local_only is False:
                all_tool_images.registry.update()

        local_tool_images = all_tool_images.local.elements

        if local_only is True:
            registry_tool_images = []
        else:
            registry_tool_images = all_tool_images.registry.elements

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

    def get_registry_only_tool_images(self, all_tool_images: ToolImages, 
                                      update_tool_image_store: bool) -> set:
        """ Get the list of registry only tool images.
        
            Returns with the list of registry only tool images.
        """
        registry_only_tool_images: set = set()
        self.check_image_availability(all_tool_images, update_tool_image_store)
        for tool in self.tools:
            if tool["image_status"] == ToolImages.REGISTRY_ONLY:
                registry_only_tool_images.add(tool["image_name"] + ':' + tool["image_version"])

        return registry_only_tool_images

    def get_deserialized(self, omit_is_installed: bool = False) -> dict[str, str]:
        """ Create the deserialized json. 
        
            Return the Dev Env as a dict.
        """
        dev_env_json_deserialized: dict = {
            "name": self.name,
            "tools": self.tools
        }
        
        if omit_is_installed is False:
            if self.is_installed:
                dev_env_json_deserialized["installed"] = "True"
            else:
                dev_env_json_deserialized["installed"] = "False"

        return dev_env_json_deserialized

    def export(self, path: str) -> None:
        """ Export the Dev Env to a file.
        
            Args:
                path -- the path of the file to export the Dev Env to
        """
        with open(path, "w") as file:
            json.dump(self.get_deserialized(True), file, indent=4)