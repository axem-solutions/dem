"""CLI command implementation for deleting a Dev Env Catalog."""
# dem/cli/command/del_cat_cmd.py

from dem.core.platform import DevEnvLocalSetup
from dem.cli.console import stdout, stderr

def execute(catalog_name: str) -> None:
    """ Delete the Dev Env Catalog.
        Args:
            catalog_name -- name of the catalog to delete
    """
    platform = DevEnvLocalSetup()

    for catalog_config in platform.dev_env_catalogs.list_catalog_configs():
        if catalog_config["name"] == catalog_name:
            platform.dev_env_catalogs.delete_catalog(catalog_config)
            stdout.print("[green]The input catalog has been successfully deleted.")
            break
    else:
        stderr.print("[red]Error: The input catalog name doesn't exist![/]")