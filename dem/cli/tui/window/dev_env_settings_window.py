"""The DevEnv Settings Screen for the TUI."""
# dem/cli/tui/window/dev_env_settings_screen.py

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Label, SelectionList
from textual.widgets.selection_list import Selection
from textual.screen import Screen
from textual.events import Mount
from textual.binding import Binding, BindingType
from typing import ClassVar
from rich.table import Table

from dem.cli.tui.printable_tool_image import PrintableToolImage

class SelectionListVimMode(SelectionList):
    """ A SelectionList with Vim-like keybindings. """
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("j", "cursor_down", "Vim Down", show=False),
        Binding("k", "cursor_up", "Vim Up", show=False)
    ]

class DevEnvSettingsScreen(Screen):
    """ The Development Environment Settings Screen. """
    TITLE = "Development Environment Settings"

    def __init__(self, printable_tool_images: list[PrintableToolImage], 
                 already_selected_tool_images: list[str] = []) -> None:
        """ Initialize the Development Environment Settings Screen. 

        Args:
            printable_tool_images (list[PrintableToolImage]): The list of PrintableToolImage objects.
            already_selected_tool_images (list[str]): The list of already selected tool images.
        """
        super().__init__()
        self.printable_tool_images = printable_tool_images
        self.already_selected_tool_images = already_selected_tool_images

        self._create_widgets()

    def _create_widgets(self) -> None:
        """ Create the widgets. """
        dev_env_selections: list[Selection] = []
        for tool_image in self.printable_tool_images:
            if tool_image.name in self.already_selected_tool_images:
                selected = True
            else:
                selected = False

            dev_env_selections.append(Selection(tool_image.name, tool_image.name, selected))

        self.tool_image_selector_widget = SelectionListVimMode(*dev_env_selections, 
                                                                id="tool_image_selector_widget", 
                                                                classes="tool_image_selector")
        self.tool_image_selector_widget.border_title = "Select the Tool Images for the Development Environment"
        self.dev_env_status_widget = Label("", id="dev_env_status_widget", classes="dev_env_status")
        self.dev_env_status_widget.border_title = "Selected Tool Images"
        self.cancel_button = Button("Cancel", id=self.app.cancel_button_id, classes="cancel_button")
        self.save_button = Button("Save", id=self.app.save_button_id, classes="save_button")

    def compose(self) -> ComposeResult:
        """ Compose the screen. 

        Returns:
            ComposeResult: The composed screen.
        """
        yield Header()
        with Container(id="dev_env_settings_screen", classes="dev_env_settings_screen"):
            yield self.tool_image_selector_widget
            yield self.dev_env_status_widget
            with Container(id="cancel_container", classes="cancel_container"):
                yield self.cancel_button
            with Container(id="save_container", classes="save_container"):
                yield self.save_button

    def on_mount(self) -> None:
        """ Handle the mount event. """
        self.set_focus(self.tool_image_selector_widget)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """ Handle the button pressed event.

        Args:
            event (Button.Pressed): Information about the event.
        """
        self.app.last_button_pressed = event.button.id
        if (event.button.id == self.app.save_button_id) and not self.app.selected_tool_images:
            self.notify("Please select at least one Tool Image.", title="Error", severity="error")
            return

        if (event.button.id == self.app.save_button_id) and self.already_selected_tool_images:
            # The user is about to overwrite the DevEnv
            self.app.push_screen(ConfirmScreen("Are you sure you want to overwrite the Development Environment?"))
        else:
            self.app.exit()

    @on(Mount)
    @on(SelectionList.SelectedChanged)
    def update_dev_env_status(self) -> None:
        """ Update the Development Environment status. """
        selected_tool_images_table = Table(show_header=False, show_lines=False, show_edge=False)
        for tool_image in self.tool_image_selector_widget.selected:
            selected_tool_images_table.add_row(tool_image)
        self.dev_env_status_widget.update(selected_tool_images_table)
        
        self.app.selected_tool_images = self.tool_image_selector_widget.selected

class ConfirmScreen(Screen):
    """ The Confirm Screen. """
    TITLE = "Confirm"

    def __init__(self, message: str) -> None:
        """ Initialize the Confirm Screen. 

        Args:
            message (str): The message to display.
        """
        super().__init__()
        self.message = Label(message, id="confirm_message")
        self.confirm_button = Button("Confirm", id=self.app.confirm_screen_confirm_button_id, 
                                     classes="confirm_screen_buttons")
        self.save_as_button = Button("Save As", id=self.app.confirm_screen_save_as_button_id, 
                                     classes="confirm_screen_buttons")
        self.cancel_button = Button("Cancel", id="cancel_button", classes="confirm_screen_buttons")

    def compose(self) -> ComposeResult:
        """ Compose the screen."""
        with Container(id="confirm_container"):
            yield self.message
            with Container(id="confirm_buttons", classes="confirm_buttons"):
                yield self.confirm_button
                yield self.save_as_button
                yield self.cancel_button

    def on_mount(self) -> None:
        """ Handle the mount event. """
        self.set_focus(self.confirm_button)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """ Handle the button pressed event.

        Args:
            event (Button.Pressed): Information about the event.
        """
        if (event.button.id ==self.app.confirm_screen_confirm_button_id) or \
           (event.button.id == self.app.confirm_screen_save_as_button_id):
            self.app.last_button_pressed = event.button.id
            self.app.exit()
        else:
            self.app.pop_screen()

class DevEnvSettingsWindow(App):
    """ The Development Environment Settings Window. """
    CSS_PATH = "dev_env_settings_window.tcss"
    save_button_id = "save_button"
    cancel_button_id = "cancel_button"
    confirm_screen_confirm_button_id = "confirm_button"
    confirm_screen_save_as_button_id = "save_as_button"

    def __init__(self, printable_tool_images: list[PrintableToolImage], 
                 already_selected_tool_images: list[str] = []) -> None:
        """ Initialize the Development Environment Settings Window.

        Args:
            printable_tool_images (list[PrintableToolImage]): The list of PrintableToolImage objects.
            already_selected_tool_images (list[str]): The list of already selected tool images.
        """
        super().__init__()
        self.printable_tool_images = printable_tool_images
        self.already_selected_tool_images = already_selected_tool_images
        self.last_button_pressed = None
        self.selected_tool_images = []

    def on_mount(self) -> None:
        """ Handle the mount event. """
        self.push_screen(DevEnvSettingsScreen(self.printable_tool_images, 
                                              self.already_selected_tool_images))