"""info CLI command implementation."""
# dem/cli/command/info_cmd.py

from dem.core.tool_images import ToolImages
from dem.core.dev_env import DevEnv, DevEnv
from dem.cli.console import stdout, stderr
from dem.core.platform import Platform
from rich.table import Table

image_status_messages = {
    ToolImages.NOT_AVAILABLE: "[red]Error: Required image is not available![/]",
    ToolImages.LOCAL_ONLY: "Image is available locally.",
    ToolImages.REGISTRY_ONLY: "Image is available in the registry.",
    ToolImages.LOCAL_AND_REGISTRY: "Image is available locally and in the registry.",
}

def print_info(dev_env: (DevEnv | DevEnv)) -> None:

    tool_info_table = Table()
    tool_info_table.add_column("Type")
    tool_info_table.add_column("Image")
    tool_info_table.add_column("Status")
    for tool in dev_env.tools:
        tool_info_table.add_row(tool["type"], tool["image_name"] + ':' + tool["image_version"],
                                image_status_messages[tool["image_status"]])
    stdout.print(tool_info_table)

def execute(platform: Platform, arg_dev_env_name: str) -> None:
    dev_env = platform.get_dev_env_by_name(arg_dev_env_name)

    if dev_env is None:
        for catalog in platform.dev_env_catalogs.catalogs:
            catalog.request_dev_envs()
            dev_env = catalog.get_dev_env_by_name(arg_dev_env_name)
            if dev_env is not None:
                dev_env.check_image_availability(platform.tool_images)
                print_info(dev_env)
    else:
        dev_env.check_image_availability(platform.tool_images)
        print_info(dev_env)

    if dev_env is None:
        stderr.print("[red]Error: Unknown Development Environment: " + arg_dev_env_name + "[/]")