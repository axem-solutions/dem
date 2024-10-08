"""Local and registry tool images."""
# dem/core/tool_images.py

from dem.core.container_engine import ContainerEngine
from dem.core.registry import Registries
from dem.core.exceptions import ToolImageError

class ToolImage():
    (
        LOCAL_ONLY,
        REGISTRY_ONLY,
        LOCAL_AND_REGISTRY,
        NOT_AVAILABLE,
    ) = range(4)

    def __init__(self, name: str) -> None:
        """ Init the class.
        
            Args:
                name -- the name of the tool image
                
            Exceptions:
                ToolImageError -- if the name is invalid
        """
        self.name = name
        try:
            self.repository = self.name.split(":")[0]
            self.tag = self.name.split(":")[1]
        except IndexError:
            raise ToolImageError(f"Invalid tool image name: {name}")
        self.availability = self.NOT_AVAILABLE

class ToolImages():
    """ Available tool images."""
    def __init__(self, container_engine: ContainerEngine, registries: Registries) -> None:
        """ Init the class.

            The tool images will be obtained by running the update method.
        
            Args: 
                container_engine -- container engine
                registries -- registries
                update_on_instantiation -- set to false for manual update
        """
        self.container_engine = container_engine
        self.registries = registries
        self.all_tool_images: dict[str, ToolImage] = {}

    def update(self, local: bool, registry: bool, reg_selection: list[str] = []) -> None:
        """ Update the list of available tools. If the tool image already exists, it will be updated.
        
            Args:
                local -- get the local tools
                registry -- get the registry tools
        """
        registry_tool_image_names = []
        local_tool_image_names = []

        if local:
            local_tool_image_names = self.container_engine.get_local_tool_images()

        if registry:
            registry_tool_image_names = self.registries.list_repos(reg_selection)

        for tool_image_name in local_tool_image_names:
            tool_image = self.all_tool_images.get(tool_image_name, ToolImage(tool_image_name))
            if tool_image_name in registry_tool_image_names:
                tool_image.availability = ToolImage.LOCAL_AND_REGISTRY
            else:
                tool_image.availability = ToolImage.LOCAL_ONLY
            self.all_tool_images[tool_image_name] = tool_image

        for tool_image_name in registry_tool_image_names:
            if tool_image_name not in local_tool_image_names:
                tool_image = self.all_tool_images.get(tool_image_name, ToolImage(tool_image_name))
                tool_image.availability = ToolImage.REGISTRY_ONLY
                self.all_tool_images[tool_image_name] = tool_image

    def get_local_ones(self) -> dict[str, ToolImage]:
        """ Get the local tool images.
        
            Return with the local tool images.
        """
        local_tool_images = {}
        for key, tool_image in self.all_tool_images.items():
            if ((tool_image.availability == ToolImage.LOCAL_ONLY) or 
                (tool_image.availability == ToolImage.LOCAL_AND_REGISTRY)):
                local_tool_images[key] = tool_image

        return local_tool_images
    
    def get_registry_ones(self) -> dict[str, ToolImage]:
        """ Get the registry tool images.
        
            Return with the registry tool images.
        """
        registry_tool_images = {}
        for key, tool_image in self.all_tool_images.items():
            if ((tool_image.availability == ToolImage.REGISTRY_ONLY) or 
                (tool_image.availability == ToolImage.LOCAL_AND_REGISTRY)):
                registry_tool_images[key] = tool_image

        return registry_tool_images