"""Menu TUI renderable."""
# dem/cli/tui/renderable/menu.py

from dem.cli.tui.printable_tool_image import PrintableToolImage
from rich import live, table, align, panel, box
from rich.console import RenderableType

from readchar import readkey, key

class BaseMenu(table.Table):
    """ Base class for the menus.
    
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

class CancelSaveMenu(HorizontalMenu):
    """ Horizontal menu with two items: cancel and save.
    
        Class attributes:
            menu_items -- the menu items with rich text formatting
    """
    menu_items = ("[underline]cancel[/]", "[underline]save[/]")
    
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

class ToolImageMenu(VerticalMenu):
    def __init__(self, printable_tool_images: list[PrintableToolImage],
                 already_selected_tool_images: list[str]) -> None:
        super().__init__()
        self.title = "Select the tool images for the Development Environment:"
        self.add_column("Tool images", no_wrap=True)
        self.add_column("Availability", no_wrap=True)
        self.tool_image_selection = []

        for index, tool_image in enumerate(printable_tool_images):
            row_content = []
            if (index == 0):
                # Set the cursor indicator for the first element.
                row_content = "* " + tool_image.name, tool_image.status
            else:
                row_content = "  " + tool_image.name, tool_image.status

            if tool_image.name in already_selected_tool_images:
                self.tool_image_selection.append(tool_image.name)
                row_content = f"{row_content[0][:2]}[green]{row_content[0][2:]}[/]", str(row_content[1])
            
            self.add_row(*row_content)
    
    def get_table_width(self) -> int:
        return sum(self._measure_column)

    def handle_user_input(self, input: str) -> None:
        if input == key.ENTER or input == key.SPACE:
            selected_cell = self.columns[0]._cells[self.cursor_pos]

            if "[green]" in selected_cell:
                selected_cell = selected_cell.replace("[green]", "")
                selected_cell = selected_cell.replace("[/]", "")
            else:
                selected_cell = f"{selected_cell[:2]}[green]{selected_cell[2:]}[/]"

            self.columns[0]._cells[self.cursor_pos] = selected_cell
        else:
            super().handle_user_input(input)

    def get_selected_tool_images(self) -> list[str]:
        for cell in self.columns[0]._cells:
            tool_image_name = cell[2:].replace("[/]", "").replace("[green]", "")
            if ("[green]" in cell) and (tool_image_name not in self.tool_image_selection):
                self.tool_image_selection.append(tool_image_name)
            elif ("[green]" not in cell) and (tool_image_name in self.tool_image_selection):
                self.tool_image_selection.remove(tool_image_name)
        
        return self.tool_image_selection

class SelectMenu(VerticalMenu):
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

class DevEnvStatusPanel(table.Table):
    def __init__(self, selected_tool_images: list[str], height: int, width: int) -> None:
        super().__init__(title="Dev Env Settings")
        self.add_column("Selected Tool Images", no_wrap=True)

        if height > 10:
            height = 10

        for tool_image in selected_tool_images:
            self.add_row(tool_image)

        if len(selected_tool_images) < height:
            for _ in range(height - len(selected_tool_images)):
                self.add_row(" " * width)