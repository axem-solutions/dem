"""CLI command implementation for deleting a Host."""
# dem/cli/command/del_host_cmd.py

from dem.core.platform import Platform
from dem.cli.console import stdout, stderr

def execute(platform: Platform, host_name: str) -> None:
    """ Delete the Host.

        Args:
            host_name -- name of the host to delete
    """
    for host_config in platform.hosts.list_host_configs():
        if host_config["name"] == host_name:
            platform.hosts.delete_host(host_config)
            stdout.print("[green]Host deleted successfully![/]")
            break
    else:
        stderr.print("[red]Error: The input Host does not exist.[/]")