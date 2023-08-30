"""CLI command implementation for adding a catalog."""
# dem/cli/command/add_cat_cmd.py

from dem.core.platform import DevEnvLocalSetup
from dem.cli.console import stdout

def execute(name: str, url:str) -> None:
    """ Add a new Dev Env Catalog.
    
        Args:
            name -- name of the catalog
            url -- URL of the catalog's JSON file
    """
    platform = DevEnvLocalSetup()
    catalog_config = {
        "name": name,
        "url": url
    }
    if catalog_config not in platform.dev_env_catalogs.list_catalog_configs():
        platform.dev_env_catalogs.add_catalog(catalog_config)
    else:
        stdout.print("[yellow]The input catalog is already added.[/]")