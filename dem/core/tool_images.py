"""Local and registry tool images."""
# dem/core/tool_images.py

import dem.core.container_engine as container_engine
import dem.core.registry as registry

class ToolImages():
    """The available tool images for a Dev Env.
    
    Provides the list of tool images available locally and in the registry.
    """
    (
        LOCAL_ONLY,
        REGISTRY_ONLY,
        LOCAL_AND_REGISTRY,
        NOT_AVAILABLE,
    ) = range(4)

    def __init__(self) -> None:
        """Init the ToolImages class with the up to date image statuses."""
        self.elements = {}
        self.container_egine = container_engine.ContainerEngine()

        self.update()

    def update(self) -> None:
        """Update the image statuses based on the local and registry tool availability."""
        self.elements = {}

        for local_image in self.container_egine.get_local_tool_images():
            self.elements[local_image] = self.LOCAL_ONLY

        for registry_image in registry.list_repos(self.container_egine):
            if registry_image in self.elements:
                self.elements[registry_image] = self.LOCAL_AND_REGISTRY
            else:
                self.elements[registry_image] = self.REGISTRY_ONLY