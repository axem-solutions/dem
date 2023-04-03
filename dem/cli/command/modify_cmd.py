"""modify CLI command implementation."""
# dem/cli/command/modify_cmd

import dem.core.data_management as data_management
from dem.core.dev_env_setup import DevEnvLocalSetup, DevEnvLocal, DevEnv
from dem.cli.console import stderr
from dem.cli.menu import ToolTypeMenu

def get_modifications_from_user(dev_env: DevEnvLocal) -> None:
    already_selected_tool_types = []
    for tool in dev_env.tools:
        already_selected_tool_types.append(tool["type"])
    tool_type_menu = ToolTypeMenu(list(DevEnv.supported_tool_types))
    tool_type_menu.preset_selection(already_selected_tool_types)

    tool_type_menu.wait_for_user()

def execute(dev_env_name: str) -> None:
    derserialized_local_dev_nev = data_management.read_deserialized_dev_env_json()
    dev_env_local_setup = DevEnvLocalSetup(derserialized_local_dev_nev)
    dev_env = dev_env_local_setup.get_dev_env_by_name(dev_env_name)
    if dev_env is None:
        stderr.print("[red]The Development Environment doesn't exist.")
    else:
        get_modifications_from_user(dev_env)