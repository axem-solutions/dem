"""A class representing a tool image with its printable availability."""
# dem/cli/tui/printable_tool_image.py

from dem.core.tool_images import ToolImage

tool_image_statuses = {
    ToolImage.LOCAL_ONLY: "local",
    ToolImage.REGISTRY_ONLY: "registry",
    ToolImage.LOCAL_AND_REGISTRY: "local and registry"
}

class PrintableToolImage():
    def __init__ (self, tool_image: ToolImage):
        self.name = tool_image.name
        self.status = tool_image_statuses[tool_image.availability]

def convert_to_printable_tool_images(all_tool_images: dict[str, ToolImage]) -> list[PrintableToolImage]:
    printable_tool_images = []
    for tool_image in all_tool_images.values():
        printable_tool_images.append(PrintableToolImage(tool_image))

    return printable_tool_images