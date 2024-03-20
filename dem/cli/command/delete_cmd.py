"""delete CLI command implementation."""
# dem/cli/command/delete_cmd.py

from dem.core.platform import Platform
from dem.core.dev_env import DevEnv
from dem.core.exceptions import PlatformError
from dem.cli.console import stderr, stdout
import typer

def execute(platform: Platform, dev_env_name: str) -> None:
    dev_env_to_delete: DevEnv | None = platform.get_dev_env_by_name(dev_env_name)

    if dev_env_to_delete is None:
        stderr.print(f"[red]Error: The [bold]{dev_env_name}[/bold] Development Environment doesn't exist.")
    else:
        if dev_env_to_delete.is_installed:
            typer.confirm("The Development Environment is installed. Do you want to uninstall it?", 
                          abort=True)

            try:
                platform.uninstall_dev_env(dev_env_to_delete)
            except PlatformError as e:
                stderr.print(f"[red]{str(e)}[/]")
                return

        stdout.print("Deleting the Development Environment...")
        platform.local_dev_envs.remove(dev_env_to_delete)
        platform.flush_descriptors()
        stdout.print(f"[green]Successfully deleted the {dev_env_name}![/]")