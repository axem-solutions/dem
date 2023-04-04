"""Local and registry tool images."""
# dem/core/tool_images.py

import dem.core.container_engine as container_engine
import dem.core.registry as registry

class ToolImages():
    (
        LOCAL_ONLY,
        REGISTRY_ONLY,
        LOCAL_AND_REGISTRY,
        NOT_AVAILABLE,
    ) = range(4)

    def __init__(self) -> None:
        self.elements = {}

        container_engine_obj = container_engine.ContainerEngine()
        local_images = container_engine_obj.get_local_tool_images()
        registry_images = registry.list_repos()

        for local_image in local_images:
            self.elements[local_image] = self.LOCAL_ONLY

        for registry_image in registry_images:
            if registry_image in self.elements:
                self.elements[registry_image] = self.LOCAL_AND_REGISTRY
            else:
                self.elements[registry_image] = self.REGISTRY_ONLY