"""CLI command implementation for listing the available registries."""
# dem/cli/command/add_reg_cmd.py

from dem.core.dev_env_setup import DevEnvLocalSetup
from dem.cli.console import stdout
from rich.table import Table

def execute() -> None:
    """ List available registries."""
    local_platform = DevEnvLocalSetup()
    registry = None
    table = Table()
    table.add_column("name")
    table.add_column("url")

    for registry in local_platform.registries.list_registries():
        table.add_row(registry["name"], registry["url"])
    
    if registry is None:
        stdout.print("[yellow]No available registries![/]")
    else:
        stdout.print(table)