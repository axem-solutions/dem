"""Image selector panel."""
# dem/cli/tui/panel/image_selector.py

from dem.cli.tui.renderable.menu import ToolImageMenu, DevEnvStatusPanel, CancelSaveMenu
from dem.cli.tui.printable_tool_image import PrintableToolImage
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from rich.live import Live
from rich.table import Table
from readchar import readkey, key

class NavigationHint(Panel):
    hint_text = """
- [bold]move cursor[/]: up and down arrows or j and k keys
- [bold]toggle selection[/]: space or enter
- [bold]jump between save/cancel and the selector[/]: tab
"""
    def __init__(self) -> None:
        super().__init__(self.hint_text, title="Navigation", expand=False)

class ErrorMessage(Table):
    def __init__(self, message: str) -> None:
        message = f"[red]{message}[/]"
        super().__init__(message, box=None, expand=False, show_edge=False)

class DevEnvSettingsWindow():
    def __init__(self, printable_tool_images: list[PrintableToolImage], 
                 already_selected_tool_images: list[str] = []) -> None:
        # Panel content
        self.dev_env_status_height = len(printable_tool_images)
        self.dev_env_status_width = 0
        for printable_tool_image in printable_tool_images:
            if len(printable_tool_image.name) > self.dev_env_status_width:
                self.dev_env_status_width = len(printable_tool_image.name)

        self.tool_image_menu = ToolImageMenu(printable_tool_images, already_selected_tool_images)
        self.dev_env_status_panel = DevEnvStatusPanel(already_selected_tool_images, 
                                                      self.dev_env_status_height, 
                                                      self.dev_env_status_width)
        self.cancel_save_menu = CancelSaveMenu()
        self.navigation_hint_panel = NavigationHint()
        self.error_message_panel = None

        self.build_layout()
        self.cancel_save_menu.remove_cursor()
        self.active_menu = self.tool_image_menu

    def build_layout(self) -> None:
        # Set the alignments
        aligned_tool_image_menu = Align(self.tool_image_menu, vertical="bottom", align="right")
        aligned_dev_env_status_panel = Align(self.dev_env_status_panel, vertical="bottom", align="left")
        aligned_cancel_save_menu = Align(self.cancel_save_menu, vertical="middle", align="center")
        aligned_navigation_hint_panel = Align(self.navigation_hint_panel, vertical="top", align="center")

        if self.error_message_panel:
            aligned_error_message_panel = Align(self.error_message_panel, vertical="middle", align="center")
        else:
            aligned_error_message_panel = Align(Table(box=None), vertical="middle", align="center")

        self.layout = Layout(name="root")

        self.layout.split_column(
            Layout(name="upper_half"),
            Layout(name="lower_half"),
        )
        self.layout["upper_half"].split_row(
            Layout(name="available"),
            Layout(name="selected")
        )

        self.layout["lower_half"].split_column(
            Layout(name="cancel_save", ratio=2),
            Layout(name="navigation_hint", ratio=6),
            Layout(name="error", ratio=2),
        )

        self.layout["available"].update(aligned_tool_image_menu)
        self.layout["selected"].update(aligned_dev_env_status_panel)
        self.layout["cancel_save"].update(aligned_cancel_save_menu)
        self.layout["navigation_hint"].update(aligned_navigation_hint_panel)
        self.layout["error"].update(aligned_error_message_panel)

    def _move_console(self) -> None:
        self.active_menu.remove_cursor()

        if self.active_menu is self.tool_image_menu:
            self.active_menu = self.cancel_save_menu
        else:
            self.active_menu = self.tool_image_menu

        self.active_menu.add_cursor()

    def _handle_user_input(self, input: str, live: Live) -> None:
        self.active_menu.handle_user_input(input)

        if (self.active_menu is self.tool_image_menu) and (input in [key.ENTER, key.SPACE]):
            self.dev_env_status_panel = DevEnvStatusPanel(self.tool_image_menu.get_selected_tool_images(),
                                                        self.dev_env_status_height,
                                                        self.dev_env_status_width)
            self.build_layout()
            live.update(self.layout)
        elif (self.active_menu is self.cancel_save_menu) and (input is key.ENTER) and \
            (not self.tool_image_menu.get_selected_tool_images()) and \
            ("save" in self.cancel_save_menu.get_selection()):
            self.error_message_panel = ErrorMessage("Error: No Tool Images selected.")
            self.cancel_save_menu.is_selected = False
            self.build_layout()
            live.update(self.layout)

    def wait_for_user(self) -> None:
        with Live(self.layout, refresh_per_second=8, screen=True) as live:
            while self.cancel_save_menu.is_selected is False:
                input = readkey()
                if input is key.TAB:
                    self._move_console()

                    if self.error_message_panel:
                        self.error_message_panel = None
                        self.build_layout()
                        live.update(self.layout)
                else:
                    self._handle_user_input(input, live)