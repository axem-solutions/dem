"""Image selector panel."""
# dem/cli/tui/panel/image_selector.py

from dem.cli.tui.renderable.menu import ToolImageMenu, DevEnvStatusPanel, CancelSaveMenu
from dem.cli.tui.printable_tool_image import PrintableToolImage
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Group
from rich.align import Align
from rich.live import Live
from readchar import readkey, key

class NavigationHint(Panel):
    hint_text = """
- [bold]move cursor[/]: arrows or vi mode
- [bold]select[/]: space or enter
- [bold]jump to save/cancel[/]: tab
"""
    def __init__(self) -> None:
        super().__init__(self.hint_text, title="Navigation", expand=False)
        self.aligned_renderable = Align(self, align="center")

class DevEnvSettingsWindow():
    def __init__(self, printable_tool_images: list[PrintableToolImage], 
                 already_selected_tool_images: list[str] = []) -> None:
        # Panel content
        self.tool_image_menu = ToolImageMenu(printable_tool_images, already_selected_tool_images)
        self.dev_env_status = DevEnvStatusPanel(already_selected_tool_images)
        self.cancel_save_menu = CancelSaveMenu()
        self.navigation_hint = NavigationHint()

        self.menus = Align(Group(
            Align(self.tool_image_menu, align="center", vertical="middle"),
            Align(self.cancel_save_menu, align="center", vertical="middle"),
        ), align="center", vertical="middle")

        self.layout = Layout(name="root")

        self.layout.split_column(
            Layout(name="main"),
            Layout(name="navigation_hint", size=7),
        )
        self.layout["main"].split_row(
            Layout(name="menus"),
            Layout(name="dev_env_status", size=30)
        )

        self.layout["menus"].update(self.menus)
        self.layout["dev_env_status"].update(self.dev_env_status.aligned_renderable)
        self.layout["navigation_hint"].update(self.navigation_hint.aligned_renderable)

        self.cancel_save_menu.remove_cursor()
        self.active_menu = self.tool_image_menu

    def wait_for_user(self) -> None:
        self.selected_tool_images = []
        with Live(self.layout, refresh_per_second=8, screen=True):
            while self.cancel_save_menu.is_selected is False:
                input = readkey()
                if input is key.TAB:
                    self.active_menu.remove_cursor()

                    if self.active_menu is self.tool_image_menu:
                        self.active_menu = self.cancel_save_menu
                    else:
                        self.active_menu = self.tool_image_menu

                    self.active_menu.add_cursor()
                else:
                    self.active_menu.handle_user_input(input)

                    if (self.active_menu is self.tool_image_menu) and (input in [key.ENTER, key.SPACE]):
                        self.selected_tool_images = self.tool_image_menu.get_selected_tool_images()
                        self.dev_env_status.update_table(self.selected_tool_images)