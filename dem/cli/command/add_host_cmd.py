"""CLI command implementation for adding a host."""

from dem.core.platform import Platform
from dem.cli.console import stdout

def execute(platform: Platform, name: str, address: str) -> None:
    """ Add a new host.
    
        Args:
            name -- name of the host
            address -- IP or hostname of the host
    """
    if not name or not address:
        stdout.print("[red]Error: NAME or ADDRESS cannot be empty.[/]")
        exit(1)

    data = platform.config_file.deserialized.get("hosts", [])

    if not data:
        platform.config_file.deserialized["hosts"] = [{"name": name, "address": address}]
    else:
        # Check if the host name already exists
        existing_host = next((host for host in data if host["name"] == name), None)
        if existing_host:
            # Ask the user if they want to overwrite the existing host
            try:
                choice = input(f"Host with name {name} already exists. Do you want to overwrite it? (yes/no): ")
            except EOFError:
                stdout.print("[yellow]Host addition cancelled.[/]")
                exit(1)

            while choice.lower() not in ['yes', 'no']:
                stdout.print("[yellow]Please enter 'yes' or 'no'.[/]")
                try:
                    choice = input(f"Host with name {name} already exists. Do you want to overwrite it? (yes/no): ")
                except EOFError:
                    stdout.print("[yellow]Host addition cancelled.[/]")
                    return

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
