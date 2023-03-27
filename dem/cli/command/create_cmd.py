"""create CLI command implementation."""
# dem/cli/command/create_cmd.py

from rich import live, table, align
import sys
from dem.core.dev_env_setup import DevEnvLocalSetup
import dem.core.data_management as data_management

def execute():
    menu = table.Table()
    menu.add_column("Tool types")

    dev_env_local_setup = DevEnvLocalSetup(data_management.read_deserialized_dev_env_json())

    for dev_env in dev_env_local_setup.dev_envs:
        menu.add_row(dev_env.name)

    menu_aligment = align.Align(menu, align="center", vertical="middle")

    with live.Live(menu_aligment, refresh_per_second=4, screen=True, transient=True) as live_menu:
        while True:
            # live_menu.console.stdin 
            key = sys.stdin.read(1)
            if key == 'y':
                menu.columns[0]._cells[0] = "[yellow]demo[/]"
            elif key == 'r':
                menu.columns[0]._cells[0] = "[red]demo[/]"
