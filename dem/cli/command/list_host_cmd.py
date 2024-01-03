"""CLI command implementation for listing the available hosts."""
# dem/cli/command/list_host_cmd.py

from dem.core.platform import Platform
from dem.cli.console import stdout
from rich.table import Table

def execute(platform: Platform) -> None:
    """ List available Hosts.
    
    Usage: dem list-host
    
    """

    hosts: list[dict] = platform.hosts.list_host_configs()
    """
    Ideally, if 'hosts' is populated, it should look something like:
    hosts = [
                {'name': 'host1', 'address': 'ip_address1'}
                {'name': 'host2', 'address': 'ip_address2'}
                .... and so on
            ]
    if there are no hosts:
    hosts = [  ]
    """
    table = Table()
    table.add_column("name")
    table.add_column("address")

    if not hosts:
        stdout.print("[yellow]No available remote hosts![/]")
    else:
        for host in hosts:
            table.add_row(host['name'], host['address'])

        stdout.print(table)