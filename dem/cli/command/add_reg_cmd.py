"""CLI command implementation for adding a registry."""
# dem/cli/command/add_reg_cmd.py

from dem.core.dev_env_setup import DevEnvLocalSetup
from dem.cli.console import stdout

def execute(name: str, url:str) -> None:
    """ Add a new registry.
    
        Args:
            name -- name or IP address of the registry
            url -- API URL of the registry 
    """
    local_platform = DevEnvLocalSetup()
    registry = {
        "name": name,
        "url": url
    }
    if registry not in local_platform.registries.list_registries():
        local_platform.registries.add_registry(registry)
    else:
        stdout.print("[yellow]The input registry is already added.[/]")