"""CLI command implementation for deleting a registry."""
# dem/cli/command/del_reg_cmd.py

from dem.core.dev_env_setup import DevEnvLocalSetup
from dem.cli.console import stdout, stderr

def execute(registry_name: str) -> None:
    """ Delete the registry.
        Args:
            registry_name -- name of the registry to delete
    """
    local_platform = DevEnvLocalSetup()

    for registry in local_platform.registries.list_registries():
        if registry["name"] == registry_name:
            local_platform.registries.delete_registry(registry)
            stdout.print("[green]The input registry has been successfully deleted.")
            break
    else:
        stderr.print("[red]Error: The input registry name doesn't exist![/]")