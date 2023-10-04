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
    config_path = os.path.expanduser("~/.home/axem/dem/config.json")
    try:
        # Check if the config file exists
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = json.load(f)
        else:
            data = {"hosts": []}
        
        # Check if the host name already exists
        existing_host = next((host for host in data["hosts"] if host["name"] == name), None)
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
            data["hosts"].append({"name": name, "address": address})
        
        # Save the updated data to the config file
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        stdout.print("[green]Host added successfully![/]")
    
    except Exception as e:
        stdout.print(f"[red]Error: {e}[/]")
