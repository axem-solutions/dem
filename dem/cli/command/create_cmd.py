"""create CLI command implementation."""
# dem/cli/command/create_cmd.py

from rich import live, table, align
import sys
from dem.core.dev_env_setup import DevEnv
import dem.core.data_management as data_management
from readchar import readkey, key

class Menu(table.Table):
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

def execute():
    menu = Menu(list(DevEnv.supported_tool_types), "Tool types")
    menu_aligment = align.Align(menu, align="center", vertical="middle")

    with live.Live(menu_aligment, refresh_per_second=8, screen=True, transient=True) as live_menu:
        while True:
            match readkey():
                case key.UP | 'k':
                    menu.move_cursor(menu.CURSOR_UP)
                case key.DOWN | "j":
                    menu.move_cursor(menu.CURSOR_DOWN)
                case key.ENTER:
                    menu.toggle_select()
                    pass
