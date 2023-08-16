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

@patch.object(menu.CancelNextMenu, "add_row")
@patch.object(menu.HorizontalMenu, "__init__")
def test_CancelNextMenu(mock_super___init__, mock_add_row):
    # Run unit under test
    test_cancel_next_menu = menu.CancelNextMenu()

    # Check expectations
    mock_super___init__.assert_called_once()
    mock_add_row.assert_called_once_with(test_cancel_next_menu.cursor_off + test_cancel_next_menu.menu_items[0],
                                         test_cancel_next_menu.cursor_off + test_cancel_next_menu.menu_items[1])

@patch.object(menu.HorizontalMenu, "__init__", MagicMock())
@patch.object(menu.CancelNextMenu, "add_row", MagicMock())
@patch("dem.cli.tui.renderable.menu.key")
def test_CancelNextMenu_handle_user_input_enter(mock_key):
    # Test setup
    test_cancel_next_menu = menu.CancelNextMenu()

    # Run unit under test
    test_cancel_next_menu.handle_user_input(mock_key.ENTER)

    # Check expectations
    assert test_cancel_next_menu.is_selected is True

@patch.object(menu.HorizontalMenu, "__init__", MagicMock())
@patch.object(menu.CancelNextMenu, "add_row", MagicMock())
@patch("dem.cli.tui.renderable.menu.key", MagicMock())
@patch.object(menu.HorizontalMenu, "handle_user_input")
def test_CancelNextMenu_handle_user_input_else(mock_super_handle_user_input):
    # Test setup
    test_cancel_next_menu = menu.CancelNextMenu()
    fake_input = MagicMock()

    # Run unit under test
    test_cancel_next_menu.handle_user_input(fake_input)

    # Check expectations
    mock_super_handle_user_input.assert_called_once_with(fake_input)

@patch.object(menu.BackMenu, "add_row")
@patch.object(menu.HorizontalMenu, "__init__")
def test_BackMenu(mock_super___init__, mock_add_row):
    # Run unit under test
    test_back_next_menu = menu.BackMenu()

    # Check expectations
    mock_super___init__.assert_called_once()
    mock_add_row.assert_called_once_with(test_back_next_menu.cursor_off + test_back_next_menu.menu_item)

@patch.object(menu.HorizontalMenu, "__init__", MagicMock())
@patch.object(menu.BackMenu, "add_row", MagicMock())
@patch("dem.cli.tui.renderable.menu.key")
def test_BackMenu_handle_user_input_enter(mock_key):
    # Test setup
    test_back_next_menu = menu.BackMenu()

    # Run unit under test
    test_back_next_menu.handle_user_input(mock_key.ENTER)

    # Check expectations
    assert test_back_next_menu.is_selected is True

@patch.object(menu.VerticalMenu, "add_row")
@patch.object(menu.ToolTypeMenu, "add_column")
@patch.object(menu.VerticalMenu, "__init__")
def test_ToolTypeMenu(mock_super___init__, mock_add_column, mock_add_row):
    # Test setup
    test_supported_tool_types = [
        "test1",
        "test2",
        "test3",
        "test4",
        "test5",
    ]

    # Run unit under test
    test_tool_type_menu = menu.ToolTypeMenu(test_supported_tool_types)

    # Check expectations
    mock_super___init__.assert_called_once()
    
    calls = [
        call("Tool types"),
        call("Selected"),
    ]
    mock_add_column.assert_has_calls(calls)

    calls = []
    for index, test_tool_type in enumerate(test_supported_tool_types):
        if (index == 0):
            calls.append(call(test_tool_type_menu.cursor_on + test_tool_type, 
                              test_tool_type_menu.not_selected))
        else:
            calls.append(call(test_tool_type_menu.cursor_off + test_tool_type, 
                              test_tool_type_menu.not_selected))
    mock_add_row.assert_has_calls(calls)

def test_ToolTypeMenu_preset_selection():
    # Test setup
    test_supported_tool_types = [
        "test1",
        "test2",
        "test3",
        "test4",
        "test5",
    ]
    test_already_selected_tool_types = [
        "test1",
        "test3",
        "test5",
    ]

    test_tool_type_menu = menu.ToolTypeMenu(test_supported_tool_types)

    # Run unit under test
    test_tool_type_menu.preset_selection(test_already_selected_tool_types)

    # Check expectations
    expected_selection = [
        test_tool_type_menu.selected,
        test_tool_type_menu.not_selected,
        test_tool_type_menu.selected,
        test_tool_type_menu.not_selected,
        test_tool_type_menu.selected,
    ]
    for row_idx, cell in enumerate(test_tool_type_menu.columns[1]._cells):
        assert cell == expected_selection[row_idx]

def test_ToolTypeMenu_toggle_select():
    # Test setup
    test_supported_tool_types = [
        "test1",
    ]

    test_tool_type_menu = menu.ToolTypeMenu(test_supported_tool_types)

    # Run unit under test - not selected -> selected
    test_tool_type_menu.toggle_select()

    # Check expectations
    assert test_tool_type_menu.columns[1]._cells[test_tool_type_menu.cursor_pos] is test_tool_type_menu.selected

    # Run unit under test - selected -> not selected
    test_tool_type_menu.toggle_select()

    # Check expectations
    assert test_tool_type_menu.columns[1]._cells[test_tool_type_menu.cursor_pos] is test_tool_type_menu.not_selected

@patch.object(menu.VerticalMenu, "__init__", MagicMock())
@patch.object(menu.ToolTypeMenu, "add_column", MagicMock())
@patch.object(menu.ToolTypeMenu, "toggle_select")
@patch("dem.cli.tui.renderable.menu.key")
def test_ToolTypeMenu_handle_user_input_enter(mock_key, mock_toggle_select):
    # Test setup
    test_tool_type_menu = menu.ToolTypeMenu([])

    # Run unit under test
    test_tool_type_menu.handle_user_input(mock_key.ENTER)

    # Check expectations
    mock_toggle_select.assert_called_once()

@patch.object(menu.VerticalMenu, "__init__", MagicMock())
@patch.object(menu.ToolTypeMenu, "add_column", MagicMock())
@patch("dem.cli.tui.renderable.menu.key", MagicMock())
@patch.object(menu.VerticalMenu, "handle_user_input")
def test_ToolTypeMenu_handle_user_input_else(mock_super_handle_user_input):
    # Test setup
    test_tool_type_menu = menu.ToolTypeMenu([])
    fake_input = MagicMock()

    # Run unit under test
    test_tool_type_menu.handle_user_input(fake_input)

    # # Check expectations
    mock_super_handle_user_input.assert_called_once_with(fake_input)

def test_ToolTypeMenu_get_selected_tool_types():
    # Test setup
    test_supported_tool_types = [
        "test1",
        "test2",
        "test3",
        "test4",
        "test5",
    ]

    test_tool_type_menu = menu.ToolTypeMenu(test_supported_tool_types)
    test_tool_type_menu.columns[1]._cells[0] = test_tool_type_menu.selected
    test_tool_type_menu.columns[1]._cells[2] = test_tool_type_menu.selected
    test_tool_type_menu.columns[1]._cells[4] = test_tool_type_menu.selected

    # Run unit under test
    actual_selected_tool_types = test_tool_type_menu.get_selected_tool_types()

    # Check expectations
    expected_selected_tool_types = [
        "test1",
        "test3",
        "test5",
    ]
    assert actual_selected_tool_types == expected_selected_tool_types
