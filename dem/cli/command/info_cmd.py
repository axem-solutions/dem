"""info CLI command implementation."""
# dem/cli/command/info_cmd.py

from dem.core.tool_images import ToolImage
from dem.core.dev_env import DevEnv, DevEnv
from dem.cli.console import stdout, stderr
from dem.core.platform import Platform
from rich.table import Table

image_status_messages = {
    ToolImage.NOT_AVAILABLE: "[red]Error: Required image is not available![/]",
    ToolImage.LOCAL_ONLY: "Image is available locally.",
    ToolImage.REGISTRY_ONLY: "Image is available in the registry.",
    ToolImage.LOCAL_AND_REGISTRY: "Image is available locally and in the registry.",
}

def print_info(dev_env: DevEnv) -> None:
    """ Print information about the given Development Environment.
    
        Args:
            dev_env -- the Development Environment to print information about
    """
    tool_info_table = Table()
    tool_info_table.add_column("Image")
    tool_info_table.add_column("Status")

    for tool_image in dev_env.tool_images:
        tool_info_table.add_row(tool_image.name,
                                image_status_messages[tool_image.availability])
    stdout.print(tool_info_table)

def execute(platform: Platform, arg_dev_env_name: str) -> None:
    """ Print information about the given Development Environment.
    
        Args:
            platform -- the platform
            arg_dev_env_name -- the name of the Development Environment to print information about
    """
    platform.assign_tool_image_instances_to_all_dev_envs()

    dev_env = platform.get_dev_env_by_name(arg_dev_env_name)

    if dev_env is None:
        for catalog in platform.dev_env_catalogs.catalogs:
            catalog.request_dev_envs()
            dev_env = catalog.get_dev_env_by_name(arg_dev_env_name)
            if dev_env:
                dev_env.assign_tool_image_instances(platform.tool_images)
            break

    if dev_env is None:
        stderr.print(f"[red]Error: Unknown Development Environment: {arg_dev_env_name}[/]\n")
    else:
        print_info(dev_env)