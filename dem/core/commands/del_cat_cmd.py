"""CLI command implementation for deleting a Dev Env Catalog."""
# dem/cli/command/del_cat_cmd.py

from dem.core.platform import Platform
from dem.core.exceptions import CatalogError
from dem.cli.console import stdout, stderr

def execute(platform: Platform, catalog_name: str) -> None:
    """ Delete the Dev Env Catalog.

        Args:
            platform -- the platform
            catalog_name -- name of the catalog to delete
    """
    try:
        platform.dev_env_catalogs.delete_catalog(catalog_name)
        stdout.print(f"[green]The [bold]{catalog_name}[/bold] catalog has been successfully deleted.")
    except CatalogError as e:
        stderr.print(f"[red]{str(e)}[/]\n")
        stderr.print("[red]The catalog could not be deleted.[/]")