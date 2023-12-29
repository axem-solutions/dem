"""run CLI command implementation."""
# dem/cli/command/run_cmd.py

from dem.core.dev_env import DevEnv
from dem.core.platform import Platform
from dem.cli.console import stdout, stderr
import typer

def handle_missing_tool_images(missing_tool_images: set[str], dev_env_local: DevEnv,
                               platform: Platform) -> None:
    """ Report an error to the user that some images are not available. Ask them if the DEM should 
        try to fix the Dev Env: abort if no, pull the missing tool images if yes.
        
        Args:
            missing_tool_images -- the missing tool images
            dev_env_local -- local Dev Env
            platform -- provides the interface to pull the missing images
    """
    stderr.print("[red]Error: The following tool images are not available locally:[/]")
    for missing_tool_image in missing_tool_images:
        stderr.print("[red]" + missing_tool_image + "[/]")
    typer.confirm("Should DEM try to fix the faulty Development Environment?", abort=True)

    platform.install_dev_env(dev_env_local)
    stdout.print("[green]DEM fixed the " + dev_env_local.name + "![/]")

def execute(platform: Platform, dev_env_name: str, container_arguments: list[str]) -> None:
    """ Execute the run command in the given Dev Env context. If something is wrong with the Dev 
        Env the DEM can try to fix it.

        Args:
            dev_env_name -- name of the Development Environment
            container_arguments -- arguments passed to the container
    """
    
    dev_env_local = platform.get_dev_env_by_name(dev_env_name)

    if dev_env_local is None:
        stderr.print("[red]Error: Unknown Development Environment: " + dev_env_name + "[/]")
        raise(typer.Abort)
    else:
        # Update the tool images manually.
        Platform.update_tool_images_on_instantiation = False
        # Only the local images are needed.
        platform.tool_images.local.update()

        missing_tool_images = set()
        for tool in dev_env_local.tools:
            tool_image = tool["image_name"] + ":" + tool["image_version"]
            # Check if the required tool image exists locally.
            if tool_image not in platform.tool_images.local.elements:
                missing_tool_images.add(tool_image)

        if missing_tool_images:
            handle_missing_tool_images(missing_tool_images, dev_env_local, platform)

        platform.container_engine.run(container_arguments)