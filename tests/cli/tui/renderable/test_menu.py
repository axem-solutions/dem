"""Tests for the menu TUI renderable."""
# tests/cli/tui/renderable/test_menu.py

# Unit under test:
import dem.cli.tui.renderable.menu as menu

# Test framework
from unittest.mock import patch, MagicMock, call

def test_BaseMenu_remove_cursor():
    # Test setup
    test_base_menu = menu.BaseMenu()
    test_base_menu.add_column()
    test_base_menu.add_row(test_base_menu.cursor_on + "test")

    # Run unit under test
    test_base_menu.remove_cursor()

    # Check expectations
    expected_cell_content = test_base_menu.cursor_off + "test"
    assert test_base_menu.columns[0]._cells[0] == expected_cell_content

def test_BaseMenu_add_cursor():
    # Test setup
    test_base_menu = menu.BaseMenu()
    test_base_menu.add_column()
    test_base_menu.add_row(test_base_menu.cursor_off + "test")

    # Run unit under test
    test_base_menu.add_cursor()

    # Check expectations
    expected_cell_content = test_base_menu.cursor_on + "test"
    assert test_base_menu.columns[0]._cells[0] == expected_cell_content

def test_BaseMenu_set_title():
    # Test setup
    test_base_menu = menu.BaseMenu()
    test_title = "test_title"

    # Run unit under test
    test_base_menu.set_title(test_title)

    # Check expectations
    expected_title = test_title + "\n"
    assert test_base_menu.title == expected_title

@patch.object(menu.VerticalMenu, "add_cursor")
@patch.object(menu.VerticalMenu, "remove_cursor")
def test_VerticalMenu_move_cursor(mock_remove_cursor, mock_add_cursor):
    # Test setup
    test_vertical_menu = menu.VerticalMenu()

    test_vertical_menu.add_column()
    test_vertical_menu.add_row()
    test_vertical_menu.add_row()
    test_vertical_menu.add_row()

    # Run unit under test - move cursor down
    test_vertical_menu.move_cursor(test_vertical_menu.CURSOR_DOWN)

    # Check expectations
    assert test_vertical_menu.cursor_pos == 1

    # Run unit under test - mover cursor up
    test_vertical_menu.move_cursor(test_vertical_menu.CURSOR_UP)

    # Check expectations
    assert test_vertical_menu.cursor_pos == 0

    # Run unit under test - underflow
    test_vertical_menu.move_cursor(test_vertical_menu.CURSOR_UP)

    # Check expectations
    assert test_vertical_menu.cursor_pos == 2

    # Run unit under test - overflow
    test_vertical_menu.move_cursor(test_vertical_menu.CURSOR_DOWN)

    # Check expectations
    assert test_vertical_menu.cursor_pos == 0

    mock_remove_cursor.assert_called()
    mock_add_cursor.assert_called()

@patch.object(menu.BaseMenu, "remove_cursor")
def test_VerticalMenu_remove_cursor(mock_remove_cursor):
    # Test setup
    test_vertical_menu = menu.VerticalMenu()

    # Run unit under test
    test_vertical_menu.remove_cursor()

    # Check expectations
    mock_remove_cursor.assert_called_once_with(row=test_vertical_menu.cursor_pos)

@patch.object(menu.BaseMenu, "add_cursor")
def test_VerticalMenu_add_cursor(mock_add_cursor):
    # Test setup
    test_vertical_menu = menu.VerticalMenu()

    # Run unit under test
    test_vertical_menu.add_cursor()

    # Check expectations
    mock_add_cursor.assert_called_once_with(row=test_vertical_menu.cursor_pos)

@patch("dem.cli.tui.renderable.menu.key")
@patch.object(menu.VerticalMenu, "move_cursor")
def test_VerticalMenu_handle_user_input(mock_move_cursor, mock_key):
    # Test setup
    test_vertical_menu = menu.VerticalMenu()

    # Run unit under test
    test_vertical_menu.handle_user_input(mock_key.UP)
    test_vertical_menu.handle_user_input(mock_key.DOWN)
    test_vertical_menu.handle_user_input('k')
    test_vertical_menu.handle_user_input('j')

    # Check expectations
    calls = [
        call(test_vertical_menu.CURSOR_UP),
        call(test_vertical_menu.CURSOR_DOWN),
        call(test_vertical_menu.CURSOR_UP),
        call(test_vertical_menu.CURSOR_DOWN),
    ]
    mock_move_cursor.assert_has_calls(calls)

@patch.object(menu.HorizontalMenu, "add_cursor")
@patch.object(menu.HorizontalMenu, "remove_cursor")
def test_HorizontalMenu_move_cursor(mock_remove_cursor, mock_add_cursor):
    # Test setup
    test_horizontal_menu = menu.HorizontalMenu()

    test_horizontal_menu.add_column()
    test_horizontal_menu.add_column()
    test_horizontal_menu.add_column()
    test_horizontal_menu.add_row()

    # Run unit under test - move cursor right
    test_horizontal_menu.move_cursor(test_horizontal_menu.CURSOR_RIGHT)

    # Check expectations
    assert test_horizontal_menu.cursor_pos == 1

    # Run unit under test - mover cursor left
    test_horizontal_menu.move_cursor(test_horizontal_menu.CURSOR_LEFT)

    # Check expectations
    assert test_horizontal_menu.cursor_pos == 0

    # Run unit under test - underflow
    test_horizontal_menu.move_cursor(test_horizontal_menu.CURSOR_LEFT)

    # Check expectations
    assert test_horizontal_menu.cursor_pos == 2

    # Run unit under test - overflow
    test_horizontal_menu.move_cursor(test_horizontal_menu.CURSOR_RIGHT)

    # Check expectations
    assert test_horizontal_menu.cursor_pos == 0

    mock_remove_cursor.assert_called()
    mock_add_cursor.assert_called()

@patch.object(menu.BaseMenu, "remove_cursor")
def test_HorizontalMenu_remove_cursor(mock_remove_cursor):
    # Test setup
    test_horizontal_menu = menu.HorizontalMenu()

    # Run unit under test
    test_horizontal_menu.remove_cursor()

    # Check expectations
    mock_remove_cursor.assert_called_once_with(column=test_horizontal_menu.cursor_pos)

@patch.object(menu.BaseMenu, "add_cursor")
def test_HorizontalMenu_add_cursor(mock_add_cursor):
    # Test setup
    test_horizontal_menu = menu.HorizontalMenu()

    # Run unit under test
    test_horizontal_menu.add_cursor()

    # Check expectations
    mock_add_cursor.assert_called_once_with(column=test_horizontal_menu.cursor_pos)

@patch("dem.cli.tui.renderable.menu.key")
@patch.object(menu.HorizontalMenu, "move_cursor")
def test_HorizontalMenu_handle_user_input(mock_move_cursor, mock_key):
    # Test setup
    test_vertical_menu = menu.HorizontalMenu()

    # Run unit under test
    test_vertical_menu.handle_user_input(mock_key.LEFT)
    test_vertical_menu.handle_user_input(mock_key.RIGHT)
    test_vertical_menu.handle_user_input('h')
    test_vertical_menu.handle_user_input('l')

    # Check expectations
    calls = [
        call(test_vertical_menu.CURSOR_LEFT),
        call(test_vertical_menu.CURSOR_RIGHT),
        call(test_vertical_menu.CURSOR_LEFT),
        call(test_vertical_menu.CURSOR_RIGHT),
    ]
    mock_move_cursor.assert_has_calls(calls)

@patch.object(menu.CancelSaveMenu, "add_row")
@patch.object(menu.HorizontalMenu, "__init__")
def test_CancelSaveMenu(mock_super___init__, mock_add_row):
    # Run unit under test
    test_cancel_next_menu = menu.CancelSaveMenu()

    # Check expectations
    mock_super___init__.assert_called_once()
    mock_add_row.assert_called_once_with(test_cancel_next_menu.cursor_off + test_cancel_next_menu.menu_items[0],
                                         test_cancel_next_menu.cursor_off + test_cancel_next_menu.menu_items[1])

@patch.object(menu.HorizontalMenu, "__init__", MagicMock())
@patch.object(menu.CancelSaveMenu, "add_row", MagicMock())
@patch("dem.cli.tui.renderable.menu.key")
def test_CancelSaveMenu_handle_user_input_enter(mock_key):
    # Test setup
    test_cancel_next_menu = menu.CancelSaveMenu()

    # Run unit under test
    test_cancel_next_menu.handle_user_input(mock_key.ENTER)

    # Check expectations
    assert test_cancel_next_menu.is_selected is True

@patch.object(menu.HorizontalMenu, "__init__", MagicMock())
@patch.object(menu.CancelSaveMenu, "add_row", MagicMock())
@patch("dem.cli.tui.renderable.menu.key", MagicMock())
@patch.object(menu.HorizontalMenu, "handle_user_input")
def test_CancelSaveMenu_handle_user_input_else(mock_super_handle_user_input):
    # Test setup
    test_cancel_next_menu = menu.CancelSaveMenu()
    fake_input = MagicMock()

    # Run unit under test
    test_cancel_next_menu.handle_user_input(fake_input)

    # Check expectations
    mock_super_handle_user_input.assert_called_once_with(fake_input)

@patch.object(menu.table.Table, "add_column")
@patch.object(menu.table.Table, "add_row")
@patch.object(menu.VerticalMenu, "__init__")
def test_ToolImageMenu(mock___init__: MagicMock, mock_add_row: MagicMock, 
                       mock_add_column: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    mock_printable_tool_image1 = MagicMock()
    mock_printable_tool_image1.name = "test_image1"
    mock_printable_tool_image1.status = "test_available1"
    mock_printable_tool_image2 = MagicMock()
    mock_printable_tool_image2.name = "test_image2"
    mock_printable_tool_image2.status = "test_available2"
    test_printable_tool_images = [mock_printable_tool_image1, mock_printable_tool_image2]

    test_already_selected_tool_images = [
        mock_printable_tool_image1.name,
        mock_printable_tool_image2.name
    ]

    # Run unit under test
    menu.ToolImageMenu(test_printable_tool_images, test_already_selected_tool_images)

    # Check expectations
    mock___init__.assert_called_once()
    mock_add_column.has_calls([
        call("Tool Image", no_wrap=True),
        call("Available", no_wrap=True)
    ])
    mock_add_row.has_calls([
        call(f"* [green]{mock_printable_tool_image1.name}[/]", mock_printable_tool_image1.status),
        call(f"  [green]{mock_printable_tool_image2.name}[/]", mock_printable_tool_image2.status)
    ])

@patch.object(menu.ToolImageMenu, "__init__")
def test_handle_user_input_when_select(mock___init__: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_input = menu.key.ENTER
    test_tool_image_menu = menu.ToolImageMenu([], [])
    test_tool_image_menu.cursor_pos = 0
    mock_columns = [MagicMock()]
    test_tool_image_menu.columns = mock_columns
    test_tool_image_menu.columns[0]._cells = []
    test_tool_image_menu.columns[0]._cells.append("* test_image")

    # Run unit under test
    test_tool_image_menu.handle_user_input(test_input)

    # Check expectations
    assert "* [green]test_image[/]" == test_tool_image_menu.columns[0]._cells[test_tool_image_menu.cursor_pos]

    mock___init__.assert_called_once()

@patch.object(menu.ToolImageMenu, "__init__")
def test_handle_user_input_when_deselect(mock___init__: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_input = menu.key.ENTER
    test_tool_image_menu = menu.ToolImageMenu([], [])
    test_tool_image_menu.cursor_pos = 0
    mock_columns = [MagicMock()]
    test_tool_image_menu.columns = mock_columns
    test_tool_image_menu.columns[0]._cells = []
    test_tool_image_menu.columns[0]._cells.append("* [green]test_image[/]")

    # Run unit under test
    test_tool_image_menu.handle_user_input(test_input)

    # Check expectations
    assert "* test_image" in test_tool_image_menu.columns[0]._cells[test_tool_image_menu.cursor_pos]

    mock___init__.assert_called_once()

@patch.object(menu.VerticalMenu, "handle_user_input")
@patch.object(menu.ToolImageMenu, "__init__")
def test_handle_user_input_when_other(mock___init__: MagicMock, mock_handle_user_input: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_input = "test_input"
    test_tool_image_menu = menu.ToolImageMenu([], [])

    # Run unit under test
    test_tool_image_menu.handle_user_input(test_input)

    # Check expectations
    mock___init__.assert_called_once()
    mock_handle_user_input.assert_called_once_with(test_input)

@patch.object(menu.ToolImageMenu, "__init__")
def test_get_selected_tool_images(mock___init__: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_tool_image_menu = menu.ToolImageMenu([], [])
    test_tool_image_menu.tool_image_selection = []
    mock_columns = [MagicMock()]
    test_tool_image_menu.columns = mock_columns
    test_tool_image_menu.columns[0]._cells = []
    test_tool_image_menu.columns[0]._cells.append("* [green]test_image1[/]")
    test_tool_image_menu.columns[0]._cells.append("  test_image2")
    test_tool_image_menu.columns[0]._cells.append("  [green]test_image3[/]")

    # Run unit under test
    actual_selected_tool_images = test_tool_image_menu.get_selected_tool_images()

    # Check expectations
    mock___init__.assert_called_once()

    assert ["test_image1", "test_image3"] == actual_selected_tool_images

@patch("dem.cli.tui.renderable.menu.align.Align")
@patch.object(menu.VerticalMenu, "add_row")
@patch.object(menu.VerticalMenu, "__init__")
def test_SelectMenu(mock___init__: MagicMock, mock_add_row: MagicMock, mock_Align: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    mock_alignment = MagicMock()
    mock_Align.return_value = mock_alignment

    test_selection = ["test1", "test2"]

    # Run unit under test
    actual_select_menu = menu.SelectMenu(test_selection)

    # Check expectations
    assert actual_select_menu.show_edge is False
    assert actual_select_menu.show_lines is False

    mock___init__.assert_called_once()
    mock_add_row.assert_has_calls([
        call("* test1"),
        call("  test2")

    ])
    mock_Align.assert_called_once_with(actual_select_menu, align="center", vertical="middle")

@patch.object(menu.SelectMenu, "move_cursor")
@patch("dem.cli.tui.renderable.menu.readkey")
@patch("dem.cli.tui.renderable.menu.live.Live")
@patch.object(menu.SelectMenu, "__init__")
def test_SelectMenu_wait_for_user(mock___init__: MagicMock, mock_Live: MagicMock, 
                                  mock_readkey: MagicMock, mock_move_cursor: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    mock_readkey.side_effect = [menu.key.UP, menu.key.DOWN, menu.key.ENTER]
    mock_alignment = MagicMock()

    test_select_menu = menu.SelectMenu([])
    test_select_menu.alignment = mock_alignment

    # Run unit under test
    test_select_menu.wait_for_user()

    # Check expectations
    mock_Live.assert_called_once_with(mock_alignment, refresh_per_second=8, screen=True)
    mock_move_cursor.assert_has_calls([
        call(test_select_menu.CURSOR_UP),
        call(test_select_menu.CURSOR_DOWN)
    ])

def test_get_selected() -> None:
    # Test setup
    test_select_menu = menu.SelectMenu([])
    test_select_menu.cursor_pos = 1
    test_select_menu.columns = [MagicMock()]
    test_select_menu.columns[0]._cells = ["* test1", "  test2"]

    # Run unit under test
    actual_selected = test_select_menu.get_selected()

    # Check expectations
    assert "test2" == actual_selected

@patch.object(menu.VerticalMenu, "set_title")
def test_set_title(mock_set_title: MagicMock) -> None:
    # Test setup
    test_select_menu = menu.SelectMenu([])
    test_select_menu.width = 0
    test_title = "test_title"

    # Run unit under test
    test_select_menu.set_title(test_title)

    # Check expectations
    assert test_select_menu.width == len(test_title)

    mock_set_title.assert_called_once_with(test_title)
    
@patch.object(menu.table.Table, "add_row")
@patch.object(menu.table.Table, "add_column")
@patch.object(menu.table.Table, "__init__")
def test_DevEnvStatusPanel(mock___init__: MagicMock, mock_add_column: MagicMock, 
                           mock_add_row: MagicMock) -> None:
    # Test setup
    mock___init__.return_value = None

    test_selected_tool_images = ["test1", "test2"]
    test_height = 12
    test_width = max(len(test_selected_tool_images[0]), len(test_selected_tool_images[1]))

    # Run unit under test
    menu.DevEnvStatusPanel(test_selected_tool_images, test_height, test_width)

    # Check expectations
    mock___init__.assert_called_once_with(title="Dev Env Settings")
    mock_add_column.assert_called_once_with("Selected Tool Images", no_wrap=True)
    mock_add_row.assert_has_calls([
        call("test1"),
        call("test2"),
    ] + [call(" " * test_width) for _ in range(8)])