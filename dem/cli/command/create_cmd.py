"""create CLI command implementation."""
# dem/cli/command/create_cmd.py

from rich import live, table, align
from dem.cli.console import stdout
import dem.core.container_engine as container_engine
import dem.core.registry as registry
from dem.core.dev_env_setup import DevEnv, DevEnvLocal, DevEnvLocalSetup
import dem.core.data_management as data_management
from readchar import readkey, key


class ToolTypeMenu(table.Table):
    (
        CURSOR_UP,
        CURSOR_DOWN
    ) = range(2)
    
    def __init__(self, elements: list[str], name: str) -> None:
        super().__init__()
        self.elements = elements
        self.cursor_pos = 0

        self.add_column(name)
        self.add_column("Selected")

        for index, element in enumerate(elements):
            if (index == 0):
                # Set the cursor indicator for the first element.
                self.add_row("* " + element)
            else:
                self.add_row("  " + element)

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

class ToolImageMenu(table.Table):
    (
        CURSOR_UP,
        CURSOR_DOWN,
    ) = range(2)

    def __init__(self, tool_images: list[list[str]], name: str) -> None:
        super().__init__()
        self.elements = tool_images
        self.cursor_pos = 0

        self.add_column(name)
        self.add_column("Availability")

        for index, tool_image in enumerate(tool_images):
            if (index == 0):
                # Set the cursor indicator for the first element.
                self.add_row("* " + tool_image[0], tool_image[1])
            else:
                self.add_row("  " + tool_image[0], tool_image[1])

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

def execute():
    tool_type_menu = ToolTypeMenu(list(DevEnv.supported_tool_types), "Tool types")
    menu_aligment = align.Align(tool_type_menu, align="center", vertical="middle")

    with live.Live(menu_aligment, refresh_per_second=8, screen=True):
        while True:
            match readkey():
                case key.UP | 'k':
                    tool_type_menu.move_cursor(tool_type_menu.CURSOR_UP)
                case key.DOWN | 'j':
                    tool_type_menu.move_cursor(tool_type_menu.CURSOR_DOWN)
                case ' ':
                    tool_type_menu.toggle_select()
                case key.ENTER:
                    break
    
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
    
    tool_image_menu = ToolImageMenu(tool_images, "Tool images")
    menu_aligment = align.Align(tool_image_menu, align="center", vertical="middle")

    dev_env_descriptor = {
        "name": "cica",
        "tools": []
    }

    with live.Live(menu_aligment, refresh_per_second=8, screen=True):
        for row_index, cell in enumerate(tool_type_menu.columns[1]._cells):
            if cell ==  "✔":
                tool_type = tool_type_menu.columns[0]._cells[row_index][2:]
                tool_image_menu.set_title("Select tool image for type " + tool_type)
                while True:
                    match readkey():
                        case key.UP | 'k':
                            tool_image_menu.move_cursor(tool_image_menu.CURSOR_UP)
                        case key.DOWN | 'j':
                            tool_image_menu.move_cursor(tool_image_menu.CURSOR_DOWN)
                        case key.ENTER:
                            break
                image = tool_image_menu.columns[0]._cells[tool_image_menu.cursor_pos][2:].split(":")
                tool_descriptor = {
                    "type": tool_type,
                    "image_name": image[0],
                    "image_version": image[1]
                }
                dev_env_descriptor["tools"].append(tool_descriptor)
    
    dev_env_local_json_deserialized = data_management.read_deserialized_dev_env_json()
    dev_env_local_setup = DevEnvLocalSetup(dev_env_local_json_deserialized)
    new_dev_env = DevEnvLocal(dev_env_descriptor)
    dev_env_local_setup.dev_envs.append(new_dev_env)
    derserialized_local_dev_nev = dev_env_local_setup.get_deserialized()
    data_management.write_deserialized_dev_env_json(derserialized_local_dev_nev)