"""CLI command implementation for adding a host."""

from dem.core.platform import DevEnvLocalSetup
from dem.cli.console import stdout
import json
import os

def execute(name: str, address: str) -> None:
    """ Add a new host.
    
        Args:
            name -- name of the host
            address -- IP or hostname of the host
    """
    
    if not name or not address:
        stdout.print("[red]Error: NAME or ADDRESS cannot be empty.[/]")
        return

    platform = DevEnvLocalSetup()
    data = platform.config_file.deserialized.get("hosts", [])  # this way the data object is a list

    if not data:
        platform.config_file.deserialized["hosts"] = [{"name": name, "address": address}]
    else:
        # Check if the host name already exists
        existing_host = next((host for host in data if host["name"] == name), None)
        if existing_host:
            # Ask the user if they want to overwrite the existing host
            while True:
                choice = input(f"Host with name {name} already exists. Do you want to overwrite it? (yes/no): ")
                if choice.lower() in ['yes', 'no']:
                    break
                stdout.print("[yellow]Please enter 'yes' or 'no'.[/]")
            
            if choice.lower() == 'yes':
                existing_host["address"] = address
            else:
                stdout.print("[yellow]Host addition cancelled.[/]")
                return
        else:
            data.append({"name": name, "address": address})

    # Save the updated data
    platform.config_file.flush()
    stdout.print("[green]Host added successfully![/]")
