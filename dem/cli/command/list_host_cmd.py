"""CLI command implementation for listing the available hosts."""
# dem/cli/command/list_reg_cmd.py

from dem.core.platform import DevEnvLocalSetup
from dem.cli.console import stdout, stderr
from rich.table import Table

def execute() -> None:
    """ List available Hosts."""
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

    platform = DevEnvLocalSetup()
    hosts = platform.config_file.deserialized.get("hosts", [])
    table = Table()
    table.add_column("name")
    table.add_column("address")

    if (len(hosts)==0) or (hosts is None):
        stderr.print("[yellow]Error: No available Hosts ![/]")
    else:
        for host in hosts:
            table.add_row(host['name'], host['address'])

        stdout.print(table)