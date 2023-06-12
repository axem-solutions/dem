"""Menu TUI renderable."""
# dem/cli/tui/renderable/menu.py

from rich import live, table, align, panel, box
from readchar import readkey, key

class BaseMenu(table.Table):
    """ Base class for the menus.
    
        Shouldn't be instantiated directly.
        
        Class attributes:
            cursor_on -- text that represents the cursor
            cursor_off -- the cursor is not in this cell
    """
    cursor_on = "* "
    cursor_off = "  "

    def __init__(self, box: box.Box | None = box.HEAVY_HEAD) -> None:
        """ Construct the BaseMenu based on the rich's Table class.
        
            Args:
                box -- how to draw the table's edges (None: no outline)
        """
        super().__init__(box=box)
        self.cursor_pos = 0

    def remove_cursor(self, column: int = 0, row: int = 0) -> None:
        """ Remove the cursor from the given cell.
        
            Args:
                column -- the column index
                row -- the row index
        """
        cell = self.columns[column]._cells[row].replace(self.cursor_on, self.cursor_off, 1)
        self.columns[column]._cells[row] = cell

    def add_cursor(self, column: int = 0, row: int = 0) -> None:
        """ Add the cursor to the given cell.
        
            Args:
                column -- the column index
                row -- the row index
        """
        cell = self.columns[column]._cells[row].replace(self.cursor_off, self.cursor_on, 1)
        self.columns[column]._cells[row] = cell

    def set_title(self, title: str) -> None:
        """ Set the text above the menu.
        
            Args:
                title -- the text to set
        """
        self.title = title + "\n"

class VerticalMenu(BaseMenu):
    """ Menu with vertical navigation.
    
        Shouldn't be instantiated directly.
        
        Class attributes:
            CURSOR_UP -- move cursor upwards
            CURSOR_DOWN -- move cursor downwards
    """
    (
        CURSOR_UP,
        CURSOR_DOWN
    ) = range(2)

    def __init__(self) -> None:
        """ Construct a VerticalMenu based on the BaseMenu."""
        super().__init__()

    def move_cursor(self, cursor_direction: int) -> None:
        """ Move the cursor in the given direction.
        
            Args:
                cursor_direction -- which direction to move
        """
        self.remove_cursor()

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

        self.add_cursor()
 
    def remove_cursor(self) -> None:
        """ Remove the cursor."""
        super().remove_cursor(row=self.cursor_pos)

    def add_cursor(self) -> None:
        """ Add the cursor."""
        super().add_cursor(row=self.cursor_pos)

    def handle_user_input(self, input: str) -> None:
        """ Handle user input.
        
            Args:
                input -- the user input (handle up/down arrows, j and k)
        """
        match input:
            case key.UP | 'k':
                self.move_cursor(self.CURSOR_UP)
            case key.DOWN | 'j':
                self.move_cursor(self.CURSOR_DOWN)

class HorizontalMenu(BaseMenu):
    """ Menu with horizontal navigation.
    
        Shouldn't be instantiated directly.
        
        Class attributes:
            CURSOR_LEFT -- move cursor left
            CURSOR_RIGHT -- move cursor right
    """
    (
        CURSOR_LEFT,
        CURSOR_RIGHT
    ) = range(2)

    def __init__(self) -> None:
        """ Construct a HorizontalMenu based on the BaseMenu."""
        super().__init__(box=None)

    def move_cursor(self, cursor_direction: int) -> None:
        """ Move the cursor in the given direction.
        
            Args:
                cursor_direction -- which direction to move
        """
        self.remove_cursor()

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

        self.add_cursor()

    def remove_cursor(self) -> None:
        """ Remove the cursor."""
        super().remove_cursor(column=self.cursor_pos)

    def add_cursor(self) -> None:
        """ Add the cursor."""
        super().add_cursor(column=self.cursor_pos)

    def handle_user_input(self, input:str) -> None:
        """ Handle user input.
        
            Args:
                input -- the user input (handle left/right arrows, h and l)
        """
        match input:
            case key.LEFT | 'h':
                self.move_cursor(self.CURSOR_LEFT)
            case key.RIGHT | 'l':
                self.move_cursor(self.CURSOR_RIGHT)

class CancelNextMenu(HorizontalMenu):
    """ Horizontal menu with two items: cancel and next.
    
        Class attributes:
            menu_items -- the menu items with rich text formatting
    """
    menu_items = ("[underline]cancel[/]", "[underline]next[/]")
    
    def __init__(self) -> None:
        """ Construct a HorizontalMenu with 2 columns and 1 row."""
        super().__init__()
        self.add_row(self.cursor_off + self.menu_items[0], 
                     self.cursor_off + self.menu_items[1])
        self.is_selected = False

    def handle_user_input(self, input: str) -> None:
        """ Handle user input or pass to parent.
        
            Args:
                input -- the user input (handle enter)
        """
        if input == key.ENTER:
            self.is_selected = True
        else:
            super().handle_user_input(input)

    def get_selection(self) -> str:
        """ Get the selected item.
        
            Return with the selected item.
        """
        return self.columns[self.cursor_pos]._cells[0]

class BackMenu(HorizontalMenu):
    """ Horizontal menu with a single item: back.
    
        Class attributes:
            menu_item -- the menu item with rich text formatting
    """
    menu_item = "[underline]back[/]"

    def __init__(self) -> None:
        """ Construct a HorizontalMenu with 1 column and 1 row."""
        super().__init__()
        self.add_row(self.cursor_off + self.menu_item)
        self.is_selected = False

    def handle_user_input(self, input: str) -> None:
        """ Handle user input.
        
            Args:
                input -- the user input (handle enter)
        """
        if input is key.ENTER:
            self.is_selected = True

class ToolTypeMenu(VerticalMenu):
    """ Vertical menu for the tool type selection.
    
        Class attributes:
            selected -- selected text
            not_selected -- not selected text
    """
    selected = "[green]yes[/]"
    not_selected = "no"

    def __init__(self, supported_tool_types: list[str]) -> None:
        """ Construct a VerticalMenu with 2 columns and rows that contain the supported tool types.
        
            Args:
                supported_tool_types -- the supported tool types
        """
        super().__init__()
        self.add_column("Tool types")
        self.add_column("Selected")

        for index, tool_type in enumerate(supported_tool_types):
            if (index == 0):
                # Set the cursor indicator for the first element.
                self.add_row(self.cursor_on + tool_type, self.not_selected)
            else:
                self.add_row(self.cursor_off + tool_type, self.not_selected)

    def preset_selection(self, already_selected: list[str]) -> None:
        """ Preset the given tool types.
        
            Args:
                already_selected -- list of tool types to set as selected
        """
        for row_idx, cell in enumerate(self.columns[0]._cells):
            if cell[2:] in already_selected:
                self.columns[1]._cells[row_idx] = self.selected

    def toggle_select(self) -> None:
        """ Toggle selection at the cursor's position. """
        if (self.columns[1]._cells[self.cursor_pos] is self.selected):
            self.columns[1]._cells[self.cursor_pos] = self.not_selected
        else:
            self.columns[1]._cells[self.cursor_pos] = self.selected

    def handle_user_input(self, input: str) -> None:
        """ Handle user input or pass to parent.
        
            Args:
                input -- the user input (handle enter or space)
        """
        if (input == key.ENTER) or (input == ' '):
            self.toggle_select()
        else:
            super().handle_user_input(input)

    def get_selected_tool_types(self) -> list[str]:
        """ Get selected tool types.

            Returns with a list of tool types that are in selected state.
        """
        selected_tool_types = []
        for row_index, cell in enumerate(self.columns[1]._cells):
            if cell == self.selected:
                selected_tool_types.append(self.columns[0]._cells[row_index][2:])
        return selected_tool_types

class ToolImageMenu(VerticalMenu):
    def __init__(self, tool_images: list[list[str]]) -> None:
        super().__init__()
        self.add_column("Tool images", no_wrap=True)
        self.add_column("Availability", no_wrap=True)

        for index, tool_image in enumerate(tool_images):
            if (index == 0):
                # Set the cursor indicator for the first element.
                self.add_row("* " + tool_image[0], tool_image[1])
            else:
                self.add_row("  " + tool_image[0], tool_image[1])

        self.is_selected = False

    def handle_user_input(self, input: str) -> None:
        if input == key.ENTER:
            self.is_selected = True
        else:
            super().handle_user_input(input)

    def get_selected_tool_image(self) -> str:
        return self.columns[0]._cells[self.cursor_pos][2:]

class SelectMenu(VerticalMenu):
    def __init__(self, selection: list[str]) -> None:
        super().__init__()
        self.alignment = align.Align(self, align="center", vertical="middle")
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

class DevEnvStatus(panel.Panel):
    def __init__(self, tool_types: list[str]) -> None:
        self.outer_table = table.Table(box=None)
        super().__init__(self.outer_table, title="Development Environment", expand=False)
        self.aligned_renderable = align.Align(self, vertical="middle")
        
        self._fill_table(tool_types)
    
    def _fill_table(self, tool_types: list[str]) -> None:
        panel_height = 3 + len(tool_types) * 4
        self.height = panel_height

        for tool_type in tool_types:
            inner_table = table.Table(box=None)
            inner_table.add_row("[bold]" + tool_type + ":[/]")
            inner_table.add_row("<not selected>")
            inner_table.add_row("")

            self.outer_table.add_row(inner_table)

    def reset_table(self, tool_types: list[str]) -> None:
        self.outer_table = table.Table(box=None)
        self._fill_table(tool_types)
        self.renderable = self.outer_table

    def set_tool_image(self, tool_selection: dict) -> None:
        for tool_type, tool_image in tool_selection.items():
            for row in self.outer_table.columns[0].cells:
                if tool_type in row.columns[0]._cells[0]:
                    row.columns[0]._cells[1] = tool_image