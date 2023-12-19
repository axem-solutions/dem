"""CLI command implementation for listing the available registries."""
# dem/cli/command/list_reg_cmd.py

from dem.core.platform import Platform
from dem.cli.console import stdout
from rich.table import Table

def execute(platform: Platform) -> None:
    """ List available registries."""
    registry = None
    table = Table()
    table.add_column("name")
    table.add_column("url")

    for registry in platform.registries.list_registry_configs():
        table.add_row(registry["name"], registry["url"])
    
    if registry is None:
        stdout.print("[yellow]No available registries![/]")
    else:
        stdout.print(table)