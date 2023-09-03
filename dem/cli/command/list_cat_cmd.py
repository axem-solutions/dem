"""CLI command implementation for listing the available Development Environment Catalogs."""
# dem/cli/command/list_cat_cmd.py

from dem.core.platform import DevEnvLocalSetup
from dem.cli.console import stdout
from rich.table import Table

def execute() -> None:
    """ List available Development Environment Catalogs."""
    platform = DevEnvLocalSetup()
    catalog_config = None
    table = Table()
    table.add_column("name")
    table.add_column("url")

    for catalog_config in platform.dev_env_catalogs.list_catalog_configs():
        table.add_row(catalog_config["name"], catalog_config["url"])
    
    if catalog_config is None:
        stdout.print("[yellow]No Development Environment Catalogs are available![/]")
    else:
        stdout.print(table)