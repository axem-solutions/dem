"""Implementation of the set-default command."""
# dem/cli/command/set_default_cmd.py

from dem.core.platform import Platform
from dem.cli.console import stderr, stdout

def execute(platform: Platform, dev_env_name: str) -> None:
    """Execute the set-default command.

    Args:
        platform (Platform): The platform instance.
        dev_env_name (str): The name of the Development Environment to set as default.
    """
    dev_env = platform.get_dev_env_by_name(dev_env_name)
    if dev_env is None:
        stderr.print(f"[red]Error: The {dev_env_name} Development Environment does not exist.[/]")
        return
    if not dev_env.is_installed:
        stderr.print(f"[red]Error: The {dev_env_name} Development Environment is not installed.[/]")
        stdout.print("Only installed Development Environments can be set as default.")
        return
    platform.default_dev_env_name = dev_env_name
    platform.flush_dev_env_properties()
    stdout.print(f"[green]The default Development Environment is now set to {dev_env_name}![/]")