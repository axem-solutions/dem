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
- [bold]move cursor[/]: arrows or vi mode
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
        self.cancel_next_menu.remove_cursor()

        self.menus = Align(Group(
            Align(self.tool_type_menu, align="center", vertical="middle"),
            Align(self.cancel_next_menu, align="center", vertical="middle"),
        ), align="center", vertical="middle")

        self.navigation_hint = NavigationHint()

        self.layout = Layout(name="root")
        self.layout.split(
            Layout(name="menus"),
            Layout(name="info", size=8),
        )
        self.layout["menus"].update(self.menus)
        self.layout["info"].update(self.navigation_hint.get_renderable())

        self.no_tool_type_selected_error = Align(Panel("[yellow]You need to select at least one tool type![/]"),
                                                 align="center", vertical="middle")
        
        self.active_menu = self.tool_type_menu

    def wait_for_user(self) -> None:
        with Live(self.layout, refresh_per_second=8, screen=True):
            selection = ""
            is_error_presented = False
            while selection == "":
                input = readkey()
                if input is key.TAB:
                    if is_error_presented is True:
                        self.layout["info"].update(self.navigation_hint.get_renderable())
                    self.active_menu.remove_cursor()

                    if self.active_menu is self.tool_type_menu:
                        self.active_menu = self.cancel_next_menu
                    else:
                        self.active_menu = self.tool_type_menu

                    self.active_menu.add_cursor()
                else:
                    self.active_menu.handle_user_input(input)

                    if self.cancel_next_menu.is_selected is True:
                        selection = self.cancel_next_menu.get_selection()

                        if ("next" in selection) and (len(self.tool_type_menu.get_selected_tool_types()) == 0):
                            self.cancel_next_menu.is_selected = False
                            self.layout["info"].update(self.no_tool_type_selected_error)
                            is_error_presented = True
                            selection = ""