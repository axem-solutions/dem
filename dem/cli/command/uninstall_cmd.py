"""uninstall CLI command implementation."""
# dem/cli/command/uninstall_cmd.py

from dem.core.dev_env import DevEnv
from dem.core.platform import Platform, PlatformError
from dem.cli.console import stderr, stdout

def execute(platform: Platform, dev_env_name: str) -> None:
    """
        Uninstall the given Development Environment.
        
        Args:
            platform -- the platform
            dev_env_name -- the name of the Development Environment to uninstall
    """
    dev_env_to_uninstall: DevEnv | None = platform.get_dev_env_by_name(dev_env_name)

    if dev_env_to_uninstall is None:
        stderr.print(f"[red]Error: The {dev_env_name} Development Environment does not exist.[/]")
    elif not dev_env_to_uninstall.is_installed:
        stderr.print(f"[red]Error: The {dev_env_name} Development Environment is not installed.[/]")
    else:
        try:
            platform.uninstall_dev_env(dev_env_to_uninstall)
        except PlatformError as e:
            stderr.print(f"[red]{str(e)}[/]")
        else:
            stdout.print(f"[green]Successfully uninstalled the {dev_env_name}![/]")