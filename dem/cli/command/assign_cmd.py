"""Implementation of the assign command."""
# dem/cli/command/assign_cmd.py

import os
from dem.core.platform import Platform
from dem.core.dev_env import DevEnv
from dem.cli.console import stderr, stdout

def execute(platform: Platform, dev_env_name: str, project_path: str) -> None:
    """Assign the given Development Environment to the given project.

        Args:
            platform -- the platform
            dev_env_name -- the name of the Development Environment to assign
            project_path -- the path to the project to assign the Development Environment to
    """
    if not os.path.isdir(project_path):
        stderr.print(f"[red]Error: The {project_path} path does not exist.[/]")
        return

    dev_env_to_assign: DevEnv | None = platform.get_dev_env_by_name(dev_env_name)

    if dev_env_to_assign is None:
        stderr.print(f"[red]Error: The {dev_env_name} Development Environment does not exist.[/]")
    else:
        platform.assign_dev_env(dev_env_to_assign, project_path)
        stdout.print(f"\n[green]Successfully assigned the {dev_env_name} Dev Env to the project at{project_path}![/]")