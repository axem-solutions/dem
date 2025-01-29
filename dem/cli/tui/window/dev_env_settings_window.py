"""The DevEnv Settings Screen for the TUI."""
# dem/cli/tui/window/dev_env_settings_screen.py

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Label, SelectionList, Input
from textual.widgets.selection_list import Selection
from textual.widgets.option_list import OptionDoesNotExist
from textual.screen import Screen
from textual.binding import Binding, BindingType
from typing import ClassVar, cast
from rich.table import Table

from dem.cli.tui.printable_tool_image import PrintableToolImage

class SelectionListVimMode(SelectionList):
    """ A SelectionList with Vim-like keybindings. """
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("j", "cursor_down", "Vim Down", show=False),
        Binding("k", "cursor_up", "Vim Up", show=False)
    ]

class ToolImageSelectorContainer(Container):
    """ A Container for the Tool Image Selector. """
    BORDER_TITLE = "Tool Image Selector"

class SelectionWithState(Selection):
    """ A Selection with a state. """
    def __init__(self, prompt: str, value: str, is_selected: bool, id: int) -> None:
        """ Initialize the SelectionWithState.

        Args:
            prompt -- the text to display
            value -- the value of the selection
            is_selected -- whether the selection is selected
            id -- the id of the selection
        """
        super().__init__(prompt, value, is_selected, id)
        self.is_selected = is_selected

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
        self.dev_env_selections: list[SelectionWithState] = []

        self._create_widgets()

    def _create_widgets(self) -> None:
        """ Create the widgets. """
        for index, tool_image in enumerate(self.printable_tool_images):
            if tool_image.name in self.already_selected_tool_images:
                selected = True
            else:
                selected = False

            self.dev_env_selections.append(SelectionWithState(tool_image.name, tool_image.name, 
                                                              selected, index))

        self.tool_image_selector_widget = SelectionListVimMode(*self.dev_env_selections, 
                                                                id="tool_image_selector_widget", 
                                                                classes="tool_image_selector")
        self.dev_env_status_widget = Label("", id="dev_env_status_widget", classes="dev_env_status")
        self.dev_env_status_widget.border_title = "Selected Tool Images"
        self.cancel_button_widget = Button("Cancel", id=self.app.cancel_button_id, classes="cancel_button")
        self.save_button_widget = Button("Save", id=self.app.save_button_id, classes="save_button")
        self.search_input_widget = Input(placeholder="Search tool images...", id="search_input")

    def compose(self) -> ComposeResult:
        """ Compose the screen. 

        Returns:
            ComposeResult: The composed screen.
        """
        yield Header()
        with Container(id="dev_env_settings_screen", classes="dev_env_settings_screen"):
            with ToolImageSelectorContainer(id="tool_image_selector_container", 
                                            classes="tool_image_selector_container"):
                yield self.search_input_widget
                yield self.tool_image_selector_widget
            yield self.dev_env_status_widget
            with Container(id="cancel_container", classes="cancel_container"):
                yield self.cancel_button_widget
            with Container(id="save_container", classes="save_container"):
                yield self.save_button_widget

    def on_mount(self) -> None:
        """ Handle the mount event. """
        self.set_focus(self.search_input_widget)

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

    @on(SelectionList.SelectedChanged)
    def update_dev_env_status(self) -> None:
        """ Update the list of selected tool images. """
        selected_tool_images_table = Table(show_header=False, show_lines=False, show_edge=False)

        self.app.selected_tool_images = []
        for selection in self.dev_env_selections:
            try:
                # Check if the selection is in the filtered widget
                self.tool_image_selector_widget.get_option(selection.id)

                # The selection is in the filtered widget, update the selection state
                if selection.value in self.tool_image_selector_widget.selected:
                    selection.is_selected = True
                else:
                    selection.is_selected = False
            except OptionDoesNotExist:
                # The selection is not in the filtered widget
                pass

            if selection.is_selected:
                self.app.selected_tool_images.append(selection.value)
                selected_tool_images_table.add_row(selection.value)
        
        self.dev_env_status_widget.update(selected_tool_images_table)

    @on(Input.Changed)
    def filter_tool_images(self, event: Input.Changed) -> None:
        """ Filter the tool images based on user input. 
            
            Args:
                event -- Information about the event. Contains the user input.
        """
        search_text = event.value.lower()
        self.tool_image_selector_widget.clear_options()

        for selection in self.dev_env_selections:
            if search_text in selection.value:
                self.tool_image_selector_widget.add_option(selection)
                if selection.is_selected:
                    self.tool_image_selector_widget.select(selection)

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
        self.selected_tool_images: list[str] = []

    def on_mount(self) -> None:
        """ Handle the mount event. """
        self.push_screen(DevEnvSettingsScreen(self.printable_tool_images, 
                                              self.already_selected_tool_images))
