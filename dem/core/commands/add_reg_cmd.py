"""CLI command implementation for adding a registry."""
# dem/cli/command/add_reg_cmd.py

from dem.core.platform import Platform
from dem.core.exceptions import RegistryError
from dem.cli.console import stdout, stderr

def execute(platform: Platform, name: str, url: str, namespace: str) -> None:
    """ Add a new registry.
    
        Args:
            name -- Unique name of the registry
            url -- API URL of the registry 
            namespace -- Namespace of the registry
    """
    
    registry = {
        "name": name,
        "namespace": namespace,
        "url": url
    }
    for registry_config in platform.registries.list_registry_configs():
        if registry_config["name"] == name:
            stderr.print("[red]Error: The input registry name is already in use![/]")
            return
    try:
        platform.registries.add_registry(registry)
        stdout.print(f"[green]The {name} registry has been successfully added![/]")
    except RegistryError as e:
        stderr.print(f"[red]Error: {str(e)}[/]")