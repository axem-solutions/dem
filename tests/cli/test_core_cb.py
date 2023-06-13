"""Tests for core callback."""
# tests/cli/test_core_cb.py

# Unit under test:
import dem.cli.core_cb as core_cb

# Test framework
from unittest.mock import patch, MagicMock, call

def test_get_value_by_key_if_exist():
    # Test setup
    test_dict = {
        "test_key": "test_value",
        "test_key_for_nested": {
            "test_key_nest": "test_nested_value",
            "test_key_nest2": "test_nested_value2"
        }
    }

    # Run unit under test
    actual_value = core_cb.get_value_by_key_if_exist(test_dict, ["test_key"])

    # Check expectations
    assert actual_value == "test_value"

    # Run unit under test
    actual_value = core_cb.get_value_by_key_if_exist(test_dict, ["invalid_key"])

    # Check expectations
    assert actual_value is None

    # Run unit under test
    actual_value = core_cb.get_value_by_key_if_exist(test_dict, ["test_key_for_nested", 
                                                                 "test_key_nest"])

    # Check expectations
    assert actual_value == "test_nested_value"

    # Run unit under test
    actual_value = core_cb.get_value_by_key_if_exist(test_dict, ["test_key_for_nested", 
                                                                 "invalid_key"])

    # Check expectations
    assert actual_value ==None

@patch("dem.cli.core_cb.stdout.print")
def test_msg_cb(mock_stdout_print):
    # Test setup
    test_msg = "test_msg"

    # Run unit under test
    core_cb.msg_cb(msg=test_msg)

    # Check expectations
    mock_stdout_print.assert_called_once_with(test_msg)

@patch("dem.cli.core_cb.stdout.rule")
def test_msg_cb(mock_stdout_rule):
    # Test setup
    test_msg = "test_msg"

    # Run unit under test
    core_cb.msg_cb(msg=test_msg, rule=True)

    # Check expectations
    mock_stdout_rule.assert_called_once_with(test_msg)

@patch("dem.cli.core_cb.typer.confirm")
@patch("dem.cli.core_cb.stdout.print")
def test_user_confirm_cb(mock_stdout_print, mock_confirm):
    # Test setup
    test_msg = "test_msg"
    test_user_confirm = "test_user_confirm"

    # Run unit under test
    core_cb.user_confirm_cb(msg=test_msg, user_confirm=test_user_confirm)

    # Check expectations
    mock_stdout_print.assert_called_once_with(test_msg)
    mock_confirm.assert_called_once_with(test_user_confirm, abort=True)

@patch("dem.cli.core_cb.get_value_by_key_if_exist")
def test_update_progress_bar(mock_get_value_by_key_if_exist):
    # Test setup
    test_tasks = {}
    test_id = "test_id"
    mock_progress = MagicMock()
    test_item = {}
    test_status = "test_status"

    test_current = 10
    test_total = 100

    mock_get_value_by_key_if_exist_return_values = [
        None,
        test_current,
        test_total
    ]

    mock_task = MagicMock()

    mock_get_value_by_key_if_exist.side_effect = mock_get_value_by_key_if_exist_return_values
    mock_progress.add_task.return_value = mock_task

    # Run unit under test
    core_cb.update_progress_bar(test_tasks, test_id, mock_progress, test_item, test_status)

    # Check expectations
    calls = [
        call(test_tasks, [test_id]),
        call(test_item, ["progressDetail", "current"]),
        call(test_item, ["progressDetail", "total"]),
    ]
    mock_get_value_by_key_if_exist.assert_has_calls = calls
    mock_progress.update.assert_called_once_with(mock_task, description=test_status, 
                                                 total=float(test_total), 
                                                 completed=float(test_current))
    
    assert test_tasks[test_id] is mock_task

@patch("dem.cli.core_cb.update_progress_bar")
@patch("dem.cli.core_cb.get_value_by_key_if_exist")
def test_process_generator_item_with_progress_detail(mock_get_value_by_key_if_exist, 
                                                     mock_update_progress_bar):
    # Test setup
    test_item = {}
    test_tasks = {}
    mock_progress = MagicMock()

    test_status = "test_status"
    test_id = "test_id"

    mock_get_value_by_key_if_exist_return_values = [
        test_status,
        test_id, 
        MagicMock()
    ]

    mock_get_value_by_key_if_exist.side_effect = mock_get_value_by_key_if_exist_return_values

    # Run unit under test
    core_cb.process_generator_item(test_item, test_tasks, mock_progress)

    # Check expectations
    calls = [
        call(test_item, ["status"]),
        call(test_item, ["id"]),
        call(test_item, ["progressDetail"]),
    ]
    mock_get_value_by_key_if_exist.assert_has_calls(calls)
    mock_update_progress_bar.assert_called_once_with(test_tasks, test_id, mock_progress, test_item,
                                                     test_status)

@patch("dem.cli.core_cb.get_value_by_key_if_exist")
def test_process_generator_item_status_with_id(mock_get_value_by_key_if_exist):
    # Test setup
    test_item = {}
    test_tasks = {}
    mock_progress = MagicMock()

    test_status = "test_status"
    test_id = "test_id"

    mock_get_value_by_key_if_exist_return_values = [
        test_status,
        test_id, 
        None
    ]

    mock_get_value_by_key_if_exist.side_effect = mock_get_value_by_key_if_exist_return_values

    # Run unit under test
    core_cb.process_generator_item(test_item, test_tasks, mock_progress)

    # Check expectations
    calls = [
        call(test_item, ["status"]),
        call(test_item, ["id"]),
        call(test_item, ["progressDetail"]),
    ]
    mock_get_value_by_key_if_exist.assert_has_calls(calls)
    mock_progress.console.print.assert_called_once_with(str(test_id) + ": " + str(test_status))

@patch("dem.cli.core_cb.get_value_by_key_if_exist")
def test_process_generator_item_status_without_id(mock_get_value_by_key_if_exist):
    # Test setup
    test_item = {}
    test_tasks = {}
    mock_progress = MagicMock()

    test_status = "test_status"

    mock_get_value_by_key_if_exist_return_values = [
        test_status,
        None
    ]

    mock_get_value_by_key_if_exist.side_effect = mock_get_value_by_key_if_exist_return_values

    # Run unit under test
    core_cb.process_generator_item(test_item, test_tasks, mock_progress)

    # Check expectations
    calls = [
        call(test_item, ["status"]),
        call(test_item, ["id"])
    ]
    mock_get_value_by_key_if_exist.assert_has_calls(calls)
    mock_progress.console.print.assert_called_once_with(str(test_status))

@patch("dem.cli.core_cb.stdout")
@patch("dem.cli.core_cb.TaskProgressColumn")
@patch("dem.cli.core_cb.BarColumn")
@patch("dem.cli.core_cb.TextColumn")
@patch("dem.cli.core_cb.process_generator_item")
@patch("dem.cli.core_cb.Progress")
def test_pull_progress_cb(mock_Progress, mock_process_generator_item, mock_TextColumn, 
                          mock_BarColumn, mock_TaskProgressColumns, mock_stdout):
    # Test setup
    mock_item = MagicMock()
    def test_generator():
        yield mock_item

    mock_progress = MagicMock()
    mock_Progress.return_value = mock_progress

    mock_layer_id_column = MagicMock()
    mock_description_column = MagicMock()

    mock_TextColumn_return_values = [
        mock_layer_id_column,
        mock_description_column
    ]
    mock_TextColumn.side_effect = mock_TextColumn_return_values

    mock_bar_column = MagicMock()
    mock_BarColumn.return_value = mock_bar_column

    mock_task_progress_column = MagicMock()
    mock_TaskProgressColumns.return_value = mock_task_progress_column

    expected_tasks = {}

    # Run unit under test
    core_cb.pull_progress_cb(generator=test_generator())

    # Check expectations
    mock_Progress.asssert_called_once_with(mock_layer_id_column, mock_description_column, 
                                           mock_bar_column, mock_task_progress_column, 
                                           console=mock_stdout)
    mock_process_generator_item.assert_called_once_with(mock_item, expected_tasks, 
                                                        mock_progress.__enter__())