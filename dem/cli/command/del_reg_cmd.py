"""CLI command implementation for deleting a registry."""
# dem/cli/command/del_reg_cmd.py

from dem.core.platform import Platform
from dem.cli.console import stdout, stderr

def execute(platform: Platform, registry_name: str) -> None:
    """ Delete the registry.
        Args:
            registry_name -- name of the registry to delete
    """
    for registry in platform.registries.list_registry_configs():
        if registry["name"] == registry_name:
            platform.registries.delete_registry(registry)
            stdout.print("[green]The input registry has been successfully deleted.")
            break
    else:
        stderr.print("[red]Error: The input registry name doesn't exist![/]")