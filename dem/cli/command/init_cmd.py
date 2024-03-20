"""Implementation of the init command."""
# dem/cli/command/init_cmd.py

import os, typer
from dem.core.platform import Platform
from dem.core.dev_env import DevEnv
from dem.core.exceptions import PlatformError
from dem.cli.console import stderr, stdout

def execute(platform: Platform, project_path: str) -> None:
    """ Initialize a project at the given path.

        Args:
            platform -- the platform
            project_path -- the path to the project to initialize
    """
    if not os.path.isdir(project_path):
        stderr.print(f"[red]Error: The {project_path} path does not exist.[/]")
        return

    try:
        dev_env = DevEnv(descriptor_path=f"{project_path}/.axem/dev_env_descriptor.json")
    except FileNotFoundError as e:
        stderr.print(f"[red]Error: No Dev Env is assigned to this project. You can assign one with `dem assign`.")
        return

    for local_dev_env in platform.local_dev_envs:
        if local_dev_env.name == dev_env.name:
            stdout.print(f"[yellow]Warning: The {dev_env.name} Development Environment is already initialized.[/]")
            typer.confirm("Would you like to re-init the Dev Env? All local changes will be lost!", abort=True)

            if local_dev_env.is_installed:
                typer.confirm("The Development Environment is installed, so it can't be deleted. Do you want to uninstall it first?", 
                              abort=True)
                
                try:
                    platform.uninstall_dev_env(local_dev_env)
                except PlatformError as e:
                    stderr.print(f"[red]{str(e)}[/]")
                    return
            
            platform.local_dev_envs.remove(local_dev_env)
            break

    platform.local_dev_envs.append(dev_env)
    platform.flush_descriptors()
    stdout.print(f"[green]Successfully initialized the {dev_env.name} Dev Env for the project at {project_path}![/]")
    stdout.print(f"\nNow you can install the Dev Env with the `dem install {dev_env.name}` command.")