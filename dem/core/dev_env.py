"""This module represents a Development Environment."""
# dem/core/dev_env.py

from dem.core.tool_images import ToolImage, ToolImages
import json, os

class DevEnv():
    """ A Development Environment. """

    def __init__(self, descriptor: dict | None = None, descriptor_path: str | None = None) -> None:
        """ Init the DevEnv class. 
        
            A new instance can be created:
            - from a Dev Env descriptor
            - from a descriptor avaialable at the given path.

            Only one of the arguments can be used at a time.
        
            Args:
                descriptor -- the description of the Development Environment from the dev_env.json 
                              file
                descriptor_path -- the path of the descriptor file

            Exceptions:
                ValueError -- if more than one of the arguments is not None
        """

        # Only one of the arguments can be not None
        if sum(arg is not None for arg in [descriptor, descriptor_path]) > 1:
            raise ValueError("Only one of the arguments can be not None.")

        if descriptor_path:
            if not os.path.exists(descriptor_path):
                raise FileNotFoundError("dev_env_descriptor.json doesn't exist.")
            with open(descriptor_path, "r") as file:
                descriptor = json.load(file)

        self.name: str = descriptor["name"]
        self.tool_image_descriptors: list[dict[str, str]] = descriptor["tools"]
        self.tool_images: list[ToolImage] = []
        descriptor_installed = descriptor.get("installed", "False")
        if "True" == descriptor_installed:
            self.is_installed = True
        else:
            self.is_installed = False

    def assign_tool_image_instances(self, tool_images: ToolImages) -> None:
        for tool_descriptor in self.tool_image_descriptors:
            tool_image_name = tool_descriptor["image_name"] + ':' + tool_descriptor["image_version"]
            tool_image = tool_images.all_tool_images.get(tool_image_name, ToolImage(tool_image_name))
            self.tool_images.append(tool_image)

    def get_deserialized(self, omit_is_installed: bool = False) -> dict[str, str]:
        """ Create the deserialized json. 
        
            Return the Dev Env as a dict.
        """
        dev_env_json_deserialized: dict = {
            "name": self.name,
            "tools": self.tool_image_descriptors
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