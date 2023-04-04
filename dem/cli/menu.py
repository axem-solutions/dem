"""Menu TUI element."""
# dem/cli/menu.py

from rich import live, table, align
from readchar import readkey, key

class Menu(table.Table):
    (
        CURSOR_UP,
        CURSOR_DOWN
    ) = range(2)

    def __init__(self) -> None:
        super().__init__()
        self.cursor_pos = 0
        self.alignment = align.Align(self, align="center", vertical="middle")

    def move_cursor(self, cursor_direction: int) -> None:
        # Remove current cursor indicator
        self.columns[0]._cells[self.cursor_pos] = self.columns[0]._cells[self.cursor_pos].replace("*", 
                                                                                                  " ", 
                                                                                                  1)
        if (cursor_direction == self.CURSOR_UP):
            if self.cursor_pos == 0:
                self.cursor_pos = self.row_count - 1
            else:
                self.cursor_pos -= 1
        else:
            if self.cursor_pos == self.row_count - 1:
                self.cursor_pos = 0
            else:
                self.cursor_pos += 1
        # Set new cursor indicator
        self.columns[0]._cells[self.cursor_pos] = self.columns[0]._cells[self.cursor_pos].replace(" ", 
                                                                                                  "*", 
                                                                                                  1)
                                                                                                
    def set_title(self, title: str) -> None:
        self.title = title

class ToolTypeMenu(Menu):
    def __init__(self, elements: list[str]) -> None:
        super().__init__()

        self.add_column("Tool types")
        self.add_column("Selected")

        for index, element in enumerate(elements):
            if (index == 0):
                # Set the cursor indicator for the first element.
                self.add_row("* " + element)
            else:
                self.add_row("  " + element)

        self.alignment = align.Align(self, align="center", vertical="middle")

    def preset_selection(self, already_selected: list[str]) -> None:
        for row_idx, cell in enumerate(self.columns[0]._cells):
            if cell[2:] in already_selected:
                self.columns[1]._cells[row_idx] = "✔"

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


class ToolImageMenu(Menu):
    def __init__(self, tool_images: list[list[str]]) -> None:
        super().__init__()

        self.add_column("Tool images")
        self.add_column("Availability")

        for index, tool_image in enumerate(tool_images):
            if (index == 0):
                # Set the cursor indicator for the first element.
                self.add_row("* " + tool_image[0], tool_image[1])
            else:
                self.add_row("  " + tool_image[0], tool_image[1])
        
        self.alignment = align.Align(self, align="center", vertical="middle")

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

    def set_cursor(self, tool_image) -> None:
        self.columns[0]._cells[self.cursor_pos] = self.columns[0]._cells[self.cursor_pos].replace("*", 
                                                                                                  " ", 
                                                                                                  1)
        for cell_idx, cell in enumerate(self.columns[0]._cells):
            if cell[2:] == tool_image:
                cell = cell.replace(" ", "*", 1)
                self.cursor_pos = cell_idx
                self.columns[0]._cells[cell_idx] = cell