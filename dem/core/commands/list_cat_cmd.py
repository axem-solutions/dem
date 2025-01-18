"""CLI command implementation for listing the available Development Environment Catalogs."""
# dem/cli/command/list_cat_cmd.py

from dem.core.platform import Platform
from dem.core.exceptions import CatalogError
from dem.cli.console import stdout, stderr
from rich.table import Table

def execute(platform: Platform) -> None:
    """ List available Development Environment Catalogs.
    
        Args:
            platform -- the platform
    """
    table = Table()
    table.add_column("name")
    table.add_column("url")

    if not platform.dev_env_catalogs.catalogs:
        stdout.print("[yellow]No Development Environment Catalogs are available![/]")
        return

    for catalog in platform.dev_env_catalogs.catalogs:
        try:
            catalog.request_dev_envs()
        except CatalogError as e:
            stderr.print(f"[red]{str(e)}[/]")

        table.add_row(catalog.name, catalog.url)

    stdout.print(table)