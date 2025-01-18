"""The clone command"""
# dem/cli/command/clone_cmd.py

import typer
from dem.core.platform import Platform
from dem.core.dev_env import DevEnv
from dem.core.exceptions import PlatformError
from dem.cli.console import stdout, stderr

def handle_existing_local_dev_env(platform: Platform, local_dev_env: DevEnv) -> None:
    """ Handle the case when the Dev Env already exists locally.

        Args:
            platform -- the platform
            local_dev_env -- the existing Dev Env
    """
    stdout.print("[yellow]The Dev Env already exists.[/]")
    typer.confirm("Continue with overwrite?", abort=True)
    
    if local_dev_env.is_installed:
        typer.confirm("The Dev Env to overwrite is installed. Do you want to uninstall it?", 
                      abort=True)
        try:
            for status in platform.uninstall_dev_env(local_dev_env):
                stdout.print(status)
        except PlatformError as e:
            stderr.print(f"[red]{str(e)}[/]")
            raise typer.Abort()

    platform.local_dev_envs.remove(local_dev_env)

def execute(platform: Platform, dev_env_name: str) -> None:
    """ Copy the Dev Env's descriptor from the catalog to the local descriptor storage.

        If the Dev Env already exists locally, the user will be asked to confirm the overwrite.

        Args:
            platform -- the platform
            dev_env_name -- name of the Dev Env to clone
    """
    catalog_dev_env: DevEnv | None = None

    if not platform.dev_env_catalogs.catalogs:
        stderr.print("[red]Error: No Development Environment Catalogs are available to clone from![/]")
        return

    for catalog in platform.dev_env_catalogs.catalogs:
        catalog.request_dev_envs()
        catalog_dev_env = catalog.get_dev_env_by_name(dev_env_name)
        if catalog_dev_env:
            break
    else:
        stderr.print("[red]Error: The input Development Environment is not available.[/]")
        return

    local_dev_env: DevEnv | None = platform.get_dev_env_by_name(dev_env_name)
    if local_dev_env:
        handle_existing_local_dev_env(platform, local_dev_env)

    platform.local_dev_envs.append(catalog_dev_env)
    platform.flush_dev_env_properties()

    stdout.print("[green]The Dev Env successfully cloned.[/]")