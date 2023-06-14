"""Image selector panel."""
# dem/cli/tui/panel/image_selector.py

from dem.cli.tui.renderable.menu import ToolImageMenu, BackMenu, DevEnvStatus
from rich.panel import Panel
from rich.layout import Layout
from rich.console import RenderableType, Group
from rich.align import Align
from rich.live import Live
from readchar import readkey, key

class NavigationHint(Panel):
    hint_text = """
- [bold]move cursor[/]: arrows or vi mode
- [bold]select[/]: space or enter
- [bold]jump to back[/]: tab
"""

    def __init__(self) -> None:
        super().__init__(self.hint_text, title="Navigation", expand=False)
        self.aligned_renderable = Align(self, align="center")

class ToolImageSelectorPanel():
    def __init__(self, elements: list[list[str]], tool_types: list[str]) -> None:
        # Panel content
        self.tool_image_menu = ToolImageMenu(elements)
        self.dev_env_status = DevEnvStatus(tool_types)
        self.back_menu = BackMenu()
        self.navigation_hint = NavigationHint()

        self.menus = Align(Group(
            Align(self.tool_image_menu, align="center", vertical="middle"),
            Align(self.back_menu, align="center", vertical="middle"),
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

        self.back_menu.remove_cursor()
        self.active_menu = self.tool_image_menu

    def wait_for_user(self) -> None:
        with Live(self.layout, refresh_per_second=8, screen=True):
            while self.active_menu.is_selected is False:
                input = readkey()
                if input is key.TAB:
                    self.active_menu.remove_cursor()

                    if self.active_menu is self.tool_image_menu:
                        self.active_menu = self.back_menu
                    else:
                        self.active_menu = self.tool_image_menu

                    self.active_menu.add_cursor()
                else:
                    self.active_menu.handle_user_input(input)