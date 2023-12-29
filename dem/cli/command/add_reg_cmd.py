"""CLI command implementation for adding a registry."""
# dem/cli/command/add_reg_cmd.py

from dem.core.platform import Platform
from dem.cli.console import stdout

def execute(platform: Platform, name: str, url:str) -> None:
    """ Add a new registry.
    
        Args:
            name -- name or IP address of the registry
            url -- API URL of the registry 
    """
    
    registry = {
        "name": name,
        "url": url
    }
    if registry not in platform.registries.list_registry_configs():
        platform.registries.add_registry(registry)
    else:
        stdout.print("[yellow]The input registry is already added.[/]")