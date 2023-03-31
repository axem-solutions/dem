"""create CLI command implementation."""
# dem/cli/command/create_cmd.py

from rich import live, table, align
import typer
from dem.cli.console import stdout
import dem.core.container_engine as container_engine
import dem.core.registry as registry
from dem.core.dev_env_setup import DevEnv, DevEnvLocal, DevEnvLocalSetup
import dem.core.data_management as data_management
from dem.cli.console import stdout
from readchar import readkey, key


class ToolTypeMenu(table.Table):
    (
        CURSOR_UP,
        CURSOR_DOWN
    ) = range(2)
    
    def __init__(self, elements: list[str]) -> None:
        super().__init__()
        self.elements = elements
        self.cursor_pos = 0

        self.add_column("Tool types")
        self.add_column("Selected")

        for index, element in enumerate(elements):
            if (index == 0):
                # Set the cursor indicator for the first element.
                self.add_row("* " + element)
            else:
                self.add_row("  " + element)

        self.alignment = align.Align(self, align="center", vertical="middle")

    def move_cursor(self, cursor_direction: int) -> None:
        # Remove current cursor indicator
        self.columns[0]._cells[self.cursor_pos] = self.columns[0]._cells[self.cursor_pos].replace("*", 
                                                                                                  " ", 
                                                                                                  1)
        if (cursor_direction == self.CURSOR_UP):
            if self.cursor_pos == 0:
                self.cursor_pos = len(self.elements) - 1
            else:
                self.cursor_pos -= 1
        else:
            if self.cursor_pos == len(self.elements) - 1:
                self.cursor_pos = 0
            else:
                self.cursor_pos += 1
        # Set new cursor indicator
        self.columns[0]._cells[self.cursor_pos] = self.columns[0]._cells[self.cursor_pos].replace(" ", 
                                                                                                  "*", 
                                                                                                  1)

    def toggle_select(self) -> None:
        if (self.columns[1]._cells[self.cursor_pos] == ""):
            self.columns[1]._cells[self.cursor_pos] = "✔"
        else:
            self.columns[1]._cells[self.cursor_pos] = ""

    def wait_for_user(self):
        with live.Live(self.alignment, refresh_per_second=8, screen=True):
            while True:
                match readkey():
                    case key.UP | 'k':
                        self.move_cursor(self.CURSOR_UP)
                    case key.DOWN | 'j':
                        self.move_cursor(self.CURSOR_DOWN)
                    case ' ':
                        self.toggle_select()
                    case key.ENTER:
                        break
            
    def get_selected_tool_types(self) -> list[str]:
        selected_tool_types = []
        for row_index, cell in enumerate(self.columns[1]._cells):
            if cell ==  "✔":
                selected_tool_types.append(self.columns[0]._cells[row_index][2:])
        return selected_tool_types


class ToolImageMenu(table.Table):
    (
        CURSOR_UP,
        CURSOR_DOWN,
    ) = range(2)

    def __init__(self, tool_images: list[list[str]]) -> None:
        super().__init__()
        self.elements = tool_images
        self.cursor_pos = 0

        self.add_column("Tool images")
        self.add_column("Availability")

        for index, tool_image in enumerate(tool_images):
            if (index == 0):
                # Set the cursor indicator for the first element.
                self.add_row("* " + tool_image[0], tool_image[1])
            else:
                self.add_row("  " + tool_image[0], tool_image[1])
        
        self.alignment = align.Align(self, align="center", vertical="middle")

    def move_cursor(self, cursor_direction: int) -> None:
        # Remove current cursor indicator
        self.columns[0]._cells[self.cursor_pos] = self.columns[0]._cells[self.cursor_pos].replace("*", 
                                                                                                  " ", 
                                                                                                  1)
        if (cursor_direction == self.CURSOR_UP):
            if self.cursor_pos == 0:
                self.cursor_pos = len(self.elements) - 1
            else:
                self.cursor_pos -= 1
        else:
            if self.cursor_pos == len(self.elements) - 1:
                self.cursor_pos = 0
            else:
                self.cursor_pos += 1
        # Set new cursor indicator
        self.columns[0]._cells[self.cursor_pos] = self.columns[0]._cells[self.cursor_pos].replace(" ", 
                                                                                                  "*", 
                                                                                                  1)
                                                                                                
    def set_title(self, title: str) -> None:
        self.title = title

    def wait_for_user(self) -> None:
        with live.Live(self.alignment, refresh_per_second=8, screen=True):
            while True:
                match readkey():
                    case key.UP | 'k':
                        self.move_cursor(self.CURSOR_UP)
                    case key.DOWN | 'j':
                        self.move_cursor(self.CURSOR_DOWN)
                    case key.ENTER:
                        break

    def get_selected_tool_image(self) -> str:
        return self.columns[0]._cells[self.cursor_pos][2:].split(":")

def dev_env_name_check(dev_env_local_setup: DevEnvLocalSetup, dev_env_name: str) -> (DevEnvLocal | None):
    for dev_env in dev_env_local_setup.dev_envs:
        if dev_env.name == dev_env_name:
            return dev_env

def get_tool_images() -> list[list[str]]:
    container_engine_obj = container_engine.ContainerEngine()
    local_images = container_engine_obj.get_local_tool_images()
    registry_images = registry.list_repos()

    tool_images = []
    for local_image in local_images:
        tool_images.append([local_image, "local"])
    for regsitry_image in registry_images:
        for image in tool_images:
            if regsitry_image == image[0]:
                image[1] = "local and regsitry"
                break
        else:
            tool_images.append([regsitry_image, "registry"])
    return tool_images

def get_dev_env_descriptor_from_user(dev_env_name: str) -> dict:
    tool_type_menu = ToolTypeMenu(list(DevEnv.supported_tool_types))
    # Wait until the user finishes the tool type selection.
    tool_type_menu.wait_for_user()
    selected_tool_types = tool_type_menu.get_selected_tool_types()

    tool_image_menu = ToolImageMenu(get_tool_images())
    dev_env_descriptor = {
        "name": dev_env_name,
        "tools": []
    }
    for tool_type in selected_tool_types:
        tool_image_menu.set_title("Select tool image for type " + tool_type)
        tool_image_menu.wait_for_user()
        selected_tool_image = tool_image_menu.get_selected_tool_image()
        tool_descriptor = {
            "type": tool_type,
            "image_name": selected_tool_image[0],
            "image_version": selected_tool_image[1]
        }
        dev_env_descriptor["tools"].append(tool_descriptor)
    return dev_env_descriptor

def execute(dev_env_name: str) -> None:
    dev_env_local_json_deserialized = data_management.read_deserialized_dev_env_json()
    dev_env_local_setup = DevEnvLocalSetup(dev_env_local_json_deserialized)
    dev_env_original = dev_env_name_check(dev_env_local_setup, dev_env_name)
    if isinstance(dev_env_original, DevEnvLocal):
        typer.confirm("The input name is already used by a Development Environment. Overwrite it?", 
                      abort=True)

    dev_env_descriptor = get_dev_env_descriptor_from_user(dev_env_name)
    
    if isinstance(dev_env_original, DevEnvLocal):
        dev_env_original.tools = dev_env_descriptor["tools"]
    else:
        new_dev_env = DevEnvLocal(dev_env_descriptor)
        dev_env_local_setup.dev_envs.append(new_dev_env)
    derserialized_local_dev_nev = dev_env_local_setup.get_deserialized()
    data_management.write_deserialized_dev_env_json(derserialized_local_dev_nev)