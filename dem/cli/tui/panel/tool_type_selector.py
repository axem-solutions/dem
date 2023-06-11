"""Tool selector panel."""
# dem/cli/tui/panel/tool_selector.py

from dem.cli.tui.renderable.menu import ToolTypeMenu, CancelNextMenu
from rich.panel import Panel
from rich.layout import Layout
from rich.console import RenderableType, Group
from rich.live import Live
from rich.align import Align
from readchar import readkey, key

class NavigationHint():
    hint_test = """
- [bold]move cursor[/]: arrows or h/j/k/l
- [bold]select[/]: space or enter
- [bold]jump to next/cancel[/]: tab
- [bold]finish selection[/]: press enter when [italic]next[/] is selected
"""

    def __init__(self) -> None:
        self.panel = Panel(self.hint_test, title="Navigation", expand=False)
        self.aligned_panel = Align(self.panel, align="center")

    def get_renderable(self) -> RenderableType:
        return self.aligned_panel

class ToolTypeSelectorPanel():
    def __init__(self, elements: list[str]) -> None:
        # Panel content
        self.tool_type_menu = ToolTypeMenu(elements)
        self.cancel_next_menu = CancelNextMenu()
        self.cancel_next_menu.hide_cursor()

        self.menus = Align(Group(
            self.tool_type_menu.alignment,
            self.cancel_next_menu.alignment,
        ), align="center", vertical="middle")

        self.navigation_hint = NavigationHint()

        self.layout = Layout(name="root")
        self.layout.split(
            Layout(name="tool_type_menu"),
            Layout(name="navigation_hint", size=8),
        )
        self.layout["tool_type_menu"].update(self.menus)
        self.layout["navigation_hint"].update(self.navigation_hint.get_renderable())
        
        self.active_menu = self.tool_type_menu

    def wait_for_user(self) -> None:
        with Live(self.layout, refresh_per_second=8, screen=True):
            # selection = ""
            while self.cancel_next_menu.is_selected is False:
                input = readkey()
                if input is key.TAB:
                    self.active_menu.hide_cursor()

                    if self.active_menu is self.tool_type_menu:
                        self.active_menu = self.cancel_next_menu
                    else:
                        self.active_menu = self.tool_type_menu

                    self.active_menu.show_cursor()
                else:
                    self.active_menu.handle_user_input(input)

                    # if self.cancel_next_menu.is_selected is True:
                    #     selection = self.cancel_next_menu.get_selection()