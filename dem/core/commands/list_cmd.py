"""list CLI command implementation."""
# dem/cli/list_cmd.py

from dem.core.platform import Platform
from dem.core.dev_env import DevEnv
from dem.core.dev_env_catalog import DevEnvCatalog
from dem.cli.console import stdout, stderr
from rich.table import Table
from typing import List

def add_dev_env_info_to_table(platform: Platform, table: Table, dev_env: DevEnv) -> None:
    """ Add Development Environment information to the table.
    
        Args:
            platform -- the Platform
            table -- the Table
            dev_env -- the Development Environment
    """
    installed_column = ""
    default_column = ""
    if dev_env.is_installed:
        dev_env.assign_tool_image_instances(platform.tool_images)
        installed_column = "[green]✓[/]"
        
        if dev_env.is_installation_correct():
            status_column = "[green]Ok[/]"
        else:
            status_column = "[red]Error: Incorrect installation![/]"

        if dev_env.name == platform.default_dev_env_name:
            default_column = "[green]✓[/]"
    else:
        status_column = "[green]Ok[/]"
    table.add_row(dev_env.name, installed_column, default_column, status_column)

def list_local_dev_envs(platform: Platform) -> None:
    """ List the local Development Environments.
    
        Args:
            platform -- the Platform
    """
    if not platform.local_dev_envs:
        stdout.print("[yellow]No Development Environment descriptors are available.[/]")
        return
    else:
        table = Table()
        table.add_column("Name")
        table.add_column("Installed", justify="center")
        table.add_column("Default", justify="center")
        table.add_column("Status", justify="center")

        for dev_env in sorted(platform.local_dev_envs, key=lambda dev_env: dev_env.name.lower()):
            add_dev_env_info_to_table(platform, table, dev_env)

        stdout.print(f"\n [italic]Local Development Environments[/]")
        stdout.print(table)

def list_actual_cat_dev_envs(catalog: DevEnvCatalog) -> None:
    """ List the Development Environments in the catalog.
    
        Args:
            catalog -- the Development Environment Catalog
    """
    catalog.request_dev_envs()
    if not catalog.dev_envs:
        stdout.print(f"[yellow]No Development Environments are available in the {catalog.name} catalog.[/]")
    else:
        table = Table()
        table.add_column("Name")
        for dev_env in catalog.dev_envs:
            table.add_row(dev_env.name)
        stdout.print(f"\n [italic]Development Environments in the {catalog.name} catalog:[/]")
        stdout.print(table)
    
def list_all_cat_dev_envs(platform: Platform) -> None:
    """ List all Development Environments in the catalogs.
    
        Args:
            platform -- the Platform
    """
    if not platform.dev_env_catalogs.catalogs:
        stdout.print("[yellow]No Development Environment Catalogs are available!")
        return
        
    for catalog in platform.dev_env_catalogs.catalogs:
        list_actual_cat_dev_envs(catalog)

def list_selected_cat_dev_envs(platform: Platform, selected_cats: List[str]) -> None:
    """ List the Development Environments from the specified catalogs.
    
        Args:
            platform -- the Platform
            selected_cats -- the specified catalogs
    """
    for cat_name in selected_cats:
        for catalog in platform.dev_env_catalogs.catalogs:
            if catalog.name == cat_name:
                list_actual_cat_dev_envs(catalog)
                break
        else:
            stderr.print(f"[red]Error: Catalog '{cat_name}' not found![/]")

def execute(platform: Platform, cat: bool, selected_cats: list[str]) -> None:
    """ List Development Environments
    
    Args:
        cat -- if true list all Development Environments in the catalogs
        selected_cats -- list the Development Environments from the specified catalogs
    """
    if cat and not selected_cats:
        list_all_cat_dev_envs(platform)
    elif selected_cats:
        list_selected_cat_dev_envs(platform, selected_cats)
    else:
        list_local_dev_envs(platform)

        if platform.default_dev_env_name:
            stdout.print(f"\n[bold]The default Development Environment: {platform.default_dev_env_name}[/]")