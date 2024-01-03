"""CLI command implementation for adding a host."""

from dem.core.platform import Platform
from dem.cli.console import stdout
import typer

def execute(platform: Platform, name: str, address: str) -> None:
    """ Add a new host.
    
        Args:
            name -- name of the host
            address -- IP or hostname of the host
    """
    existing_host: dict | None = next((host for host in platform.hosts.list_host_configs() if host["name"] == name), 
                                      None)
    if existing_host:
        typer.confirm(f"Host with name {name} already exists. Do you want to overwrite it?", 
                      abort=True)
        platform.hosts.delete_host(existing_host)

    platform.hosts.add_host({"name": name, "address": address})
    stdout.print("[green]Host added successfully![/]")