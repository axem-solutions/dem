"""Local and registry tool images."""
# dem/core/tool_images.py

from dem.core.exceptions import RegistryError
from dem.core.container_engine import ContainerEngine
from dem.core.registry import Registries

class BaseToolImages():
    """ Base class for the tool images. 
    
        Do not instantiate it directly!
    """
    def __init__(self) -> None:
        """ Init the class. """
        self.elements = []

class LocalToolImages(BaseToolImages):
    """ Local tool images."""
    def __init__(self, container_engine: ContainerEngine) -> None:
        """ Init the class.
        
            Args: 
                container_engine -- container engine
        """
        super().__init__()
        self.container_egine = container_engine

    def update(self) -> None:
        """ Update the local tool image list using the container engine."""
        self.elements = self.container_egine.get_local_tool_images()

class RegistryToolImages(BaseToolImages):
    """ Registry tool images. """

    def __init__(self, registries: Registries) -> None:
        """ Init the class.
        
            Args: 
                registries -- registries
        """
        super().__init__()
        self._registries = registries

    def update(self) -> None:
        """ Update the list of available tools in the registry using the registry interface."""
        try:
            self.elements = self._registries.list_repos()
        except RegistryError as e:
            self.elements = []
            raise

class ToolImages():
    """ Available tool images."""
    (
        LOCAL_ONLY,
        REGISTRY_ONLY,
        LOCAL_AND_REGISTRY,
        NOT_AVAILABLE,
    ) = range(4)

    def __init__(self, container_engine: ContainerEngine, registries: Registries, 
                 update_on_instantiation: bool = True) -> None:
        """ Init the class.
        
            Args: 
                container_engine -- container engine
                registries -- registries
                update_on_instantiation -- set to false for manual update
        """
        self.local = LocalToolImages(container_engine)
        self.registry = RegistryToolImages(registries)

        if update_on_instantiation is True:
            self.local.update()
            self.registry.update()