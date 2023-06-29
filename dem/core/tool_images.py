"""Local and registry tool images."""
# dem/core/tool_images.py

import dem.core.registry as registry
from dem.cli.console import stdout
from dem.core.exceptions import RegistryError
from dem.core.container_engine import ContainerEngine

class BaseToolImages():
    """The available tool images for a Dev Env.
    
    Provides the list of tool images available locally and in the registry.
    """

    def __init__(self, container_engine: ContainerEngine) -> None:
        """Init the ToolImages class with the up to date image statuses."""
        self.elements = []
        self.container_egine = container_engine

class LocalToolImages(BaseToolImages):
    def __init__(self, container_engine: ContainerEngine) -> None:
        super().__init__(container_engine)

        self.update()

    def update(self) -> None:
        self.elements = self.container_egine.get_local_tool_images()

class RegistryToolImages(BaseToolImages):
    status_start_cb = None
    status_stop_cb = None

    def __init__(self, container_engine: ContainerEngine) -> None:
        super().__init__(container_engine)

        self.update()

    def update(self) -> None:
        try:
            self.elements = registry.list_repos(self.container_egine, 
                                                  self.status_start_cb, self.status_stop_cb)
        except RegistryError as e:
            stdout.print("[red]" + str(e) + "[/]")
            stdout.print("[red]Using local tool images only![/]")
            self.elements = []

class ToolImages():
    (
        LOCAL_ONLY,
        REGISTRY_ONLY,
        LOCAL_AND_REGISTRY,
        NOT_AVAILABLE,
    ) = range(4)

    def __init__(self, container_engine: ContainerEngine) -> None:
        self.local = LocalToolImages(container_engine)
        self.registry = RegistryToolImages(container_engine)