"""CLI command implementation for adding a catalog."""
# dem/cli/command/add_cat_cmd.py

from dem.core.platform import Platform
from dem.core.exceptions import CatalogError
from dem.cli.console import stderr, stdout

def execute(platform: Platform, name: str, url:str) -> None:
    """ Add a new Dev Env Catalog.
    
        Args:
            platform -- the platform
            name -- name of the catalog
            url -- URL of the catalog's JSON file
    """
    try:
        platform.dev_env_catalogs.add_catalog(name, url)
        stdout.print("[green]The catalog has been successfully added.[/]")
    except CatalogError as e:
        stderr.print(f"[red]{str(e)}[/]\n")
        stderr.print("[red]The catalog could not be added.[/]")