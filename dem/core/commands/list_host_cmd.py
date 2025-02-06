"""CLI command implementation for listing the available hosts."""
# dem/cli/command/list_host_cmd.py

from dem.core.platform import Platform
from dem.cli.console import stdout
from rich.table import Table

def execute(platform: Platform) -> None:
    """ List available Hosts.
    
        Usage: dem list-host
        
        Ideally, if 'remote_hosts' is populated, it should look something like:
        remote_hosts = [
                    {'name': 'host1', 'address': 'ip_address1'}
                    {'name': 'host2', 'address': 'ip_address2'}
                    .... and so on
                ]
        if there are no hosts:
        remote_hosts = [  ]

        Args:
            platform -- the platform
    """
    remote_hosts: list[dict] = platform.hosts.list_host_configs()

    if not remote_hosts:
        stdout.print("[yellow]No available remote hosts![/]")

    table = Table()
    table.add_column("name")
    table.add_column("address")
    table.add_row(platform.hosts.local.name, platform.hosts.local.address)
    for host in remote_hosts:
        table.add_row(host['name'], host['address'])

    stdout.print(table)
    stdout.print("Note: The 'local' host is the host where the DEM Core is running," + \
                 "and is always available.")