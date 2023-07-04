"""Local and registry tool images."""
# dem/core/tool_images.py

import dem.core.registry as registry
from dem.cli.console import stdout
from dem.core.exceptions import RegistryError
from dem.core.container_engine import ContainerEngine

class BaseToolImages():
    """ Base class for the tool images. 
    
    Do not instantiate it directly!
    """
    def __init__(self, container_engine: ContainerEngine) -> None:
        """ Init the class.
        
        Args: 
            container_engine -- container engine
        """
        self.elements = []
        self.container_egine = container_engine

class LocalToolImages(BaseToolImages):
    """ Local tool images."""
    def __init__(self, container_engine: ContainerEngine) -> None:
        """ Init the class.
        
        Args: 
            container_engine -- container engine
        """
        super().__init__(container_engine)

    def update(self) -> None:
        """ Update the local tool image list using the container engine."""
        self.elements = self.container_egine.get_local_tool_images()

class RegistryToolImages(BaseToolImages):
    """ Registry tool images.
    
    Class attributes:
        status_start_cb -- gets called when the process has been started
        status_stop_cb -- gets called when the process has been finished
    """
    status_start_cb = None
    status_stop_cb = None

    def __init__(self, container_engine: ContainerEngine) -> None:
        """ Init the class.
        
        Args: 
            container_engine -- container engine
        """
        super().__init__(container_engine)

    def update(self) -> None:
        """ Update the list of available tools in the registry using the registry interface."""
        try:
            self.elements = registry.list_repos(self.container_egine, 
                                                  self.status_start_cb, self.status_stop_cb)
        except RegistryError as e:
            stdout.print("[red]" + str(e) + "[/]")
            stdout.print("[red]Using local tool images only![/]")
            self.elements = []

class ToolImages():
    """ Available tool images."""
    (
        LOCAL_ONLY,
        REGISTRY_ONLY,
        LOCAL_AND_REGISTRY,
        NOT_AVAILABLE,
    ) = range(4)

    def __init__(self, container_engine: ContainerEngine, update_on_instantiation: bool = True) -> None:
        """ Init the class.
        
        Args: 
            container_engine -- container engine
            update_on_instantiation -- set to false for manual update
        """
        self.local = LocalToolImages(container_engine)
        self.registry = RegistryToolImages(container_engine)

        if update_on_instantiation is True:
            self.local.update()
            self.registry.update()