"""Menu TUI element."""
# dem/cli/menu.py

from rich import live, table, align, text, panel
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
        self.hide_cursor()

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
        self.show_cursor()
                                                                                                
    def hide_cursor(self):
        self.columns[0]._cells[self.cursor_pos] = self.columns[0]._cells[self.cursor_pos].replace("*", 
                                                                                                  " ", 
                                                                                                  1)

    def show_cursor(self):
        self.columns[0]._cells[self.cursor_pos] = self.columns[0]._cells[self.cursor_pos].replace(" ", 
                                                                                                  "*", 
                                                                                                  1)

    def set_title(self, title: str) -> None:
        self.title = title + "\n"

class VerticalMenu(table.Table):
    (
        CURSOR_LEFT,
        CURSOR_RIGHT
    ) = range(2)

    def __init__(self) -> None:
        super().__init__(box=None)
        self.cursor_pos = 0
        self.alignment = align.Align(self, align="center", vertical="middle")

    def move_cursor(self, cursor_direction: int) -> None:
        # Remove current cursor indicator
        self.hide_cursor()

        if (cursor_direction == self.CURSOR_LEFT):
            if self.cursor_pos == 0:
                self.cursor_pos = len(self.columns) - 1
            else:
                self.cursor_pos -= 1
        else:
            if self.cursor_pos == len(self.columns) - 1:
                self.cursor_pos = 0
            else:
                self.cursor_pos += 1

        # Set new cursor indicator
        self.show_cursor()

    def hide_cursor(self):
        self.columns[self.cursor_pos]._cells[0] = self.columns[self.cursor_pos]._cells[0].replace("*", 
                                                                                                  " ", 
                                                                                                  1)

    def show_cursor(self):
        self.columns[self.cursor_pos]._cells[0] = self.columns[self.cursor_pos]._cells[0].replace(" ", 
                                                                                                  "*", 
                                                                                                  1)

    def set_title(self, title: str) -> None:
        self.title = title + "\n"

class CancelNextMenu(VerticalMenu):
    menu_items = ("[underline]cancel[/]", "[underline]next[/]")
    
    def __init__(self) -> None:
        super().__init__()

        self.add_row("* " + self.menu_items[0],"  " + self.menu_items[1])
        self.is_selected = False

    def handle_user_input(self, input: str) -> None:
        match input:
            case key.LEFT | 'h':
                self.move_cursor(self.CURSOR_LEFT)
            case key.RIGHT | 'l':
                self.move_cursor(self.CURSOR_RIGHT)
            case key.ENTER:
                self.is_selected = True

    def get_selection(self) -> str:
        if "* " in str(self.columns[0]._cells[0]):
            return str(self.columns[0]._cells[0])
        else:
            return str(self.columns[1]._cells[0])

class BackMenu(VerticalMenu):
    menu_item = "[underline]back[/]"

    def __init__(self) -> None:
        super().__init__()

        self.add_row("* " + self.menu_item)
        self.is_selected = False

        self.aligned_renderable = align.Align(self, align="center", vertical="middle")

    def handle_user_input(self, input: str) -> None:
        if input is key.ENTER:
            self.is_selected = True

class DevEnvStatus(panel.Panel):
    def __init__(self, tool_types: list[str]) -> None:
        self.outer_table = table.Table(box=None)
        panel_height = 3 + len(tool_types) * 4
        super().__init__(self.outer_table, title="Development Environment", expand=False, 
                         height=panel_height)
        self.aligned_renderable = align.Align(self, vertical="middle")

        for tool_type in tool_types:
            inner_table = table.Table(box=None)
            inner_table.add_row("[bold]" + tool_type + ":[/]")
            inner_table.add_row("<not selected>")
            inner_table.add_row("")

            self.outer_table.add_row(inner_table)

    def set_tool_image(self, tool_selection: dict) -> None:
        for tool_type, tool_image in tool_selection.items():
            for row in self.outer_table.columns[0].cells:
                if tool_type in row.columns[0]._cells[0]:
                    row.columns[0]._cells[1] = tool_image

class ToolTypeMenu(Menu):
    selection_status = {
        "selected": "[green]yes[/]",
        "not selected": "no",
    }

    def __init__(self, elements: list[str]) -> None:
        super().__init__()

        self.add_column("Tool types")
        self.add_column("Selected")

        for index, element in enumerate(elements):
            if (index == 0):
                # Set the cursor indicator for the first element.
                self.add_row("* " + element, self.selection_status["not selected"])
            else:
                self.add_row("  " + element, self.selection_status["not selected"])

    def preset_selection(self, already_selected: list[str]) -> None:
        for row_idx, cell in enumerate(self.columns[0]._cells):
            if cell[2:] in already_selected:
                self.columns[1]._cells[row_idx] = self.selection_status["selected"]

    def toggle_select(self) -> None:
        if (self.columns[1]._cells[self.cursor_pos] is self.selection_status["selected"]):
            self.columns[1]._cells[self.cursor_pos] = self.selection_status["not selected"]
        else:
            self.columns[1]._cells[self.cursor_pos] = self.selection_status["selected"]

    def handle_user_input(self, input: str) -> None:
        match input:
            case key.UP | 'k':
                self.move_cursor(self.CURSOR_UP)
            case key.DOWN | 'j':
                self.move_cursor(self.CURSOR_DOWN)
            case key.ENTER | ' ':
                self.toggle_select()

    def get_selected_tool_types(self) -> list[str]:
        selected_tool_types = []
        for row_index, cell in enumerate(self.columns[1]._cells):
            if cell == self.selection_status["selected"]:
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
        
        self.aligned_renderable = align.Align(self, align="center", vertical="middle")

        self.is_selected = False

    def handle_user_input(self, input: str) -> None:
        match input:
            case key.UP | 'k':
                self.move_cursor(self.CURSOR_UP)
            case key.DOWN | 'j':
                self.move_cursor(self.CURSOR_DOWN)
            case key.ENTER:
                self.is_selected = True

    def get_selected_tool_image(self) -> str:
        return self.columns[0]._cells[self.cursor_pos][2:]

    def set_cursor(self, tool_image) -> None:
        self.columns[0]._cells[self.cursor_pos] = self.columns[0]._cells[self.cursor_pos].replace("*", 
                                                                                                  " ", 
                                                                                                  1)
        for cell_idx, cell in enumerate(self.columns[0]._cells):
            if cell[2:] == tool_image:
                cell = cell.replace(" ", "*", 1)
                self.cursor_pos = cell_idx
                self.columns[0]._cells[cell_idx] = cell

class SelectMenu(Menu):
    def __init__(self, selection: list[str]) -> None:
        super().__init__()
        self.show_edge = False
        self.show_lines = False

        for index, element in enumerate(selection):
            if (index == 0):
                # Set the cursor indicator for the first element.
                self.add_row("* " + element)
            else:
                self.add_row("  " + element)

        self.alignment = align.Align(self, align="center", vertical="middle")

    def wait_for_user(self):
        with live.Live(self.alignment, refresh_per_second=8, screen=True):
            while True:
                match readkey():
                    case key.UP | 'k':
                        self.move_cursor(self.CURSOR_UP)
                    case key.DOWN | 'j':
                        self.move_cursor(self.CURSOR_DOWN)
                    case key.ENTER:
                        break
            
    def get_selected(self) -> str:
        return self.columns[0]._cells[self.cursor_pos][2:]
    
    def set_title(self, title: str) -> None:
        self.width = len(title)
        super().set_title(title)