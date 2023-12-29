"""The pull command"""
# dem/cli/command/pull_cmd.py

from dem.core.tool_images import ToolImages
from dem.core.platform import Platform
from dem.core.dev_env import DevEnv
from dem.cli.console import stdout, stderr

def create_dev_env(local_dev_env: DevEnv | None, catalog_dev_env: DevEnv, 
                            platform: Platform) -> DevEnv:
    """Install the Dev Env descriptor to the dev_env.json.
    
    If the dev_env_local is None, the Dev Env is not yet installed locally. Install it by appending 
    the Dev Env descriptor to the dev_env.json file.
    If the Dev Env is already installed, but the descriptor is different, then overwrite the 
    dev_env.json element with the new one.
    If the Dev Env is already installed and both the descriptors are the same, then there is nothing
    to do. 
    Args:
        dev_env_local -- local Dev Env instance (none if not yet installed)
        dev_env_org -- organization's Dev Env instance
        dev_env_local_setup -- the local Dev Env setup
    Return with the dev_env_local instance.
    """
    if local_dev_env is None:
        # If not available, install it.
        local_dev_env = DevEnv(dev_env_to_copy=catalog_dev_env)
        platform.local_dev_envs.append(local_dev_env)
        platform.flush_descriptors()
    elif local_dev_env.tools != catalog_dev_env.tools:
        # If already installed, but different, then overwrite it.
        local_dev_env.tools = catalog_dev_env.tools
        platform.flush_descriptors()

    return local_dev_env

def execute(platform: Platform, dev_env_name: str) -> None:
    catalog_dev_env: DevEnv | None = None

    if not platform.dev_env_catalogs.catalogs:
        stderr.print("[red]Error: No Development Environment Catalogs are available to pull the image from![/]")
        return

    for catalog in platform.dev_env_catalogs.catalogs:
        catalog_dev_env = catalog.get_dev_env_by_name(dev_env_name)
        if catalog_dev_env is not None:
            break
    else:
        stderr.print("[red]Error: The input Development Environment is not available for the organization.[/]")
        return

    local_dev_env = create_dev_env(platform.get_dev_env_by_name(catalog_dev_env.name), 
                                            catalog_dev_env, platform)

    platform.install_dev_env(local_dev_env)
    # Check image availability.
    image_statuses: list = local_dev_env.check_image_availability(platform.tool_images, 
                                                                  update_tool_image_store=True)

    if image_statuses.count(ToolImages.LOCAL_AND_REGISTRY) == len(image_statuses):
        stdout.print("The [yellow]" + local_dev_env.name + "[/] Development Environment is ready!")
    else:
        stderr.print("The installation failed.")