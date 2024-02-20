"""list CLI command implementation."""
# dem/cli/list_cmd.py

from dem.core.platform import Platform
from dem.core.dev_env import DevEnv
from dem.core.tool_images import ToolImages
from dem.cli.console import stdout, stderr
from rich.table import Table

(
    DEV_ENV_ORG_NOT_IN_REGISTRY,
    DEV_ENV_ORG_INSTALLED_LOCALLY,
    DEV_ENV_ORG_REINSTALL,
    DEV_ENV_ORG_READY,
) = range(4)

(
    DEV_ENV_LOCAL_NOT_AVAILABLE,
    DEV_ENV_LOCAL_REINSTALL,
    DEV_ENV_LOCAL_INSTALLED,
) = range(3)

dev_env_org_status_messages = {
    DEV_ENV_ORG_NOT_IN_REGISTRY: "[red]Error: Required image is not available in the registry![/]",
    DEV_ENV_ORG_INSTALLED_LOCALLY: "Installed locally.",
    DEV_ENV_ORG_REINSTALL: "Incomplete local install. The missing images are available in the registry. Use `dem pull` to reinstall.",
    DEV_ENV_ORG_READY: "Ready to be installed.",
}

dev_env_local_status_messages = {
    DEV_ENV_LOCAL_NOT_AVAILABLE: "[red]Error: Required image is not available![/]",
    DEV_ENV_LOCAL_REINSTALL: "Incomplete local install. The missing images are available in the registry. Use `dem pull` to reinstall.",
    DEV_ENV_LOCAL_INSTALLED: "Installed.",
}

def get_catalog_dev_env_status(platform: Platform, dev_env: DevEnv) -> str:
    image_statuses = dev_env.check_image_availability(platform.tool_images)
    if (ToolImages.NOT_AVAILABLE in image_statuses) or (ToolImages.LOCAL_ONLY in image_statuses):
        dev_env_status = dev_env_org_status_messages[DEV_ENV_ORG_NOT_IN_REGISTRY]
    elif (image_statuses.count(ToolImages.LOCAL_AND_REGISTRY) == len(image_statuses)) and \
            platform.get_dev_env_by_name(dev_env.name):
        dev_env_status = dev_env_org_status_messages[DEV_ENV_ORG_INSTALLED_LOCALLY]
    else:
        if platform.get_dev_env_by_name(dev_env.name):
            dev_env_status = dev_env_org_status_messages[DEV_ENV_ORG_REINSTALL]
        else:
            dev_env_status = dev_env_org_status_messages[DEV_ENV_ORG_READY]
    return dev_env_status

def get_local_dev_env_status(dev_env: DevEnv, tool_images: ToolImages) -> str:
    image_statuses = dev_env.check_image_availability(tool_images)
    if (ToolImages.NOT_AVAILABLE in image_statuses):
        dev_env_status = dev_env_local_status_messages[DEV_ENV_LOCAL_NOT_AVAILABLE]
    elif (ToolImages.REGISTRY_ONLY in image_statuses):
        dev_env_status = dev_env_local_status_messages[DEV_ENV_LOCAL_REINSTALL]
    else:
        dev_env_status = dev_env_local_status_messages[DEV_ENV_LOCAL_INSTALLED]
    return dev_env_status

def list_dev_envs(platform: Platform, local: bool, org: bool)-> None:
    table = Table()
    table.add_column("Development Environment")
    table.add_column("Status")

    if ((local == True) and (org == False)):
        if not platform.local_dev_envs:
            stdout.print("[yellow]No installed Development Environments.[/]")
            return
        else:
            for dev_env in platform.local_dev_envs:
                table.add_row(dev_env.name, get_local_dev_env_status(dev_env, platform.tool_images))
    elif((local == False) and (org == True)):
        if not platform.dev_env_catalogs.catalogs:
            stdout.print("[yellow]No Development Environment Catalogs are available!")
            return
        for catalog in platform.dev_env_catalogs.catalogs:
            catalog.request_dev_envs()
            if not catalog.dev_envs:
                stdout.print("[yellow]No Development Environments are available in the catalogs.[/]")
                return
            else:
                for dev_env in catalog.dev_envs:
                    table.add_row(dev_env.name, get_catalog_dev_env_status(platform, dev_env))
    else:
        stderr.print("[red]Error: Invalid options.[/]")
        return

    stdout.print(table)

def list_tool_images(platform: Platform, local: bool, org: bool) -> None:
    """ List tool images
    
    Args:
        local -- list local tool images
        org -- list the tool catalog
    """
    if (local == True) and (org == False):        
        local_images = platform.container_engine.get_local_tool_images()

        table = Table()
        table.add_column("Repository")
        for local_image in local_images:
            table.add_row(local_image)
        stdout.print(table)
    elif (local == False) and (org == True):
        if not platform.registries.registries:
            stdout.print("[yellow]No registries are available!")
            return

        registry_images = platform.registries.list_repos()
        if registry_images:
            table = Table()
            table.add_column("Repository")
            for registry_image in registry_images:
                table.add_row(registry_image)
            stdout.print(table)
        else:
            stdout.print("[yellow]No images are available in the registries!")

def execute(platform: Platform, local: bool, org: bool, env: bool, tool: bool) -> None:
    if ((local == True) or (org == True)) and (env == True) and (tool == False):
        list_dev_envs(platform, local, org)
    elif ((local == True) or (org == True)) and (env == False) and (tool == True):
        list_tool_images(platform, local, org)
    else:
        stderr.print(\
"""Usage: dem list [OPTIONS]
Try 'dem list --help' for help.

Error: You need to set the scope and what to list!""")