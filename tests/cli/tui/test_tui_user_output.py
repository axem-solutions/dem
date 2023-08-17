"""Tests for the TUI user output."""
# tests/cli/tui/test_tui_user_output.py

# Unit under test:
import dem.cli.tui.tui_user_output as tui_user_output

# Test framework
import pytest
from unittest.mock import patch, MagicMock, call

from typing import Generator

def test_PullProgressBar__update_progress_bar():
    # Test setup
    test_generator = MagicMock()
    test_id = "test_id"
    test_current = 10
    test_total = 100
    test_item = {
        "progressDetail": {
            "current": test_current,
            "total": test_total,
        }
    }
    test_status = "test_status"
    test_task_id = 0

    pull_progress_bar = tui_user_output.PullProgressBar(test_generator)
    pull_progress_bar.progress = MagicMock()

    pull_progress_bar.progress.add_task.return_value = test_task_id

    # Run unit under test
    pull_progress_bar._update_progress_bar(test_id, test_item, test_status)

    # Check expectations
    assert pull_progress_bar.tasks[test_id] is test_task_id

    pull_progress_bar.progress.add_task.assert_called_once_with(str(test_id), id=test_id)
    pull_progress_bar.progress.update.assert_called_once_with(test_task_id, 
                                                              description=str(test_status),
                                                              total=float(test_total),
                                                              completed=float(test_current))

@patch.object(tui_user_output.PullProgressBar, "_update_progress_bar")
def test_PullProgressBar__process(mock__update_progress_bar):
    # Test setup
    test_generator = MagicMock()
    test_status = "test_status"
    test_id = "test_id"
    test_item = {
        "status": test_status,
        "id": test_id,
        "progressDetail": MagicMock(),
    }

    pull_progress_bar = tui_user_output.PullProgressBar(test_generator)

    # Run unit under test
    pull_progress_bar._process(test_item)

    # Check expectations
    mock__update_progress_bar.assert_called_once_with(test_id, test_item, test_status)

def test_PullProgressBar__process_no_progressDetail():
    # Test setup
    test_generator = MagicMock()
    test_status = "test_status"
    test_id = "test_id"
    test_item = {
        "status": test_status,
        "id": test_id,
    }

    pull_progress_bar = tui_user_output.PullProgressBar(test_generator)
    pull_progress_bar.progress = MagicMock()

    # Run unit under test
    pull_progress_bar._process(test_item)

    # Check expectations
    pull_progress_bar.progress.console.print.assert_called_once_with(str(test_id) + ": " + str(test_status))

def test_PullProgressBar__progress_no_id():
    # Test setup
    test_generator = MagicMock()
    test_status = "test_status"
    test_item = {
        "status": test_status,
    }

    pull_progress_bar = tui_user_output.PullProgressBar(test_generator)
    pull_progress_bar.progress = MagicMock()

    # Run unit under test
    pull_progress_bar._process(test_item)

    # Check expectations
    pull_progress_bar.progress.console.print.assert_called_once_with(str(test_status))

@patch.object(tui_user_output.PullProgressBar, "_process")
@patch("dem.cli.tui.tui_user_output.stdout")
@patch("dem.cli.tui.tui_user_output.TaskProgressColumn")
@patch("dem.cli.tui.tui_user_output.BarColumn")
@patch("dem.cli.tui.tui_user_output.TextColumn")
@patch("dem.cli.tui.tui_user_output.Progress")
def test_PullProgressBar_run_generator(mock_Progress: MagicMock, mock_TextColumn: MagicMock,
                                       mock_BarColumn: MagicMock, 
                                       mock_TaskProgressColumn: MagicMock, mock_stdout: MagicMock,
                                       mock__process: MagicMock):
    # Test setup
    mock_text_column_layer_id = MagicMock()
    mock_text_column_description = MagicMock()
    mock_bar_column = MagicMock()
    mock_task_progress_column = MagicMock()

    mock_TextColumn.side_effect = [mock_text_column_layer_id, mock_text_column_description]
    mock_BarColumn.return_value = mock_bar_column
    mock_TaskProgressColumn.return_value = mock_task_progress_column

    test_items = [MagicMock(), MagicMock()]
    def mock_generator() -> Generator:
        for item in test_items:
            yield item

    pull_progress_bar = tui_user_output.PullProgressBar(mock_generator())

    # Run unit under test
    pull_progress_bar.run_generator()

    # Check expectations
    calls = [
        call("[progress.layer_id]{task.fields[id]}"),
        call("[progress.description]{task.description}"),
    ]
    mock_TextColumn.assert_has_calls(calls)
    mock_BarColumn.assert_called_once()
    mock_TaskProgressColumn.assert_called_once()

    mock_Progress.assert_called_once_with(mock_text_column_layer_id, mock_text_column_description,
                                          mock_bar_column, mock_task_progress_column, 
                                          console=mock_stdout)

    calls = []
    for item in test_items:
        calls.append(call(item))
    mock__process.assert_has_calls(calls)

@patch("dem.cli.tui.tui_user_output.stdout.print")
def test_TUIUserOutput_msg(mock_stdout_print: MagicMock):
    # Test setup
    test_text = "test_text"

    test_tui_user_output = tui_user_output.TUIUserOutput()

    # Run unit under test
    test_tui_user_output.msg(test_text)

    # Check expectations
    mock_stdout_print.assert_called_once_with(test_text)

@patch("dem.cli.tui.tui_user_output.stdout.rule")
def test_TUIUserOutput_msg_is_title(mock_stdout_rule: MagicMock):
    # Test setup
    test_text = "test_text"

    test_tui_user_output = tui_user_output.TUIUserOutput()

    # Run unit under test
    test_tui_user_output.msg(test_text, True)

    # Check expectations
    mock_stdout_rule.assert_called_once_with(test_text)

@patch("dem.cli.tui.tui_user_output.stderr.print")
def test_TUIUserOutput_error(mock_stderr_print: MagicMock):
    # Test setup
    test_text = "test_text"

    test_tui_user_output = tui_user_output.TUIUserOutput()

    # Run unit under test
    test_tui_user_output.error(test_text)

    # Check expectations
    mock_stderr_print.assert_called_once_with("[red]" + test_text + "[/]")

@patch("dem.cli.tui.tui_user_output.typer.confirm")
@patch("dem.cli.tui.tui_user_output.stdout.print")
def test_TUIUserOutput_get_confirm(mock_stdout_print: MagicMock, mock_confirm: MagicMock):
    # Test setup
    test_text = "test_text"
    test_confirm_text = "confirm_text"

    test_tui_user_output = tui_user_output.TUIUserOutput()

    # Run unit under test
    test_tui_user_output.get_confirm(test_text, test_confirm_text)

    # Check expectations
    mock_stdout_print.assert_called_once_with(test_text)
    mock_confirm.assert_called_once_with(test_confirm_text, abort=True)

@patch("dem.cli.tui.tui_user_output.PullProgressBar")
def test_TUIUserOutput_progress_generator(mock_PullProgressBar: MagicMock):
    # Test setup
    mock_generator = MagicMock()
    mock_pull_progress_bar = MagicMock()
    mock_PullProgressBar.return_value = mock_pull_progress_bar

    test_tui_user_output = tui_user_output.TUIUserOutput()

    # Run unit under test
    test_tui_user_output.progress_generator(mock_generator)

    # Check expectations
    mock_PullProgressBar.assert_called_once_with(mock_generator)
    mock_pull_progress_bar.run_generator.assert_called_once()

@patch("dem.cli.tui.tui_user_output.Status")
def test_TUIUserOutput_status_generator(mock_Status: MagicMock):
    # Test setup
    test_items = [MagicMock(), MagicMock()]
    def mock_generator() -> Generator:
        for item in test_items:
            yield item

    mock_status = MagicMock()
    mock_Status.return_value.__enter__.return_value = mock_status

    test_tui_user_output = tui_user_output.TUIUserOutput()

    # Run unit under test
    test_tui_user_output.status_generator(mock_generator())

    # Check expectations
    mock_Status.assert_called_once_with("")
    mock_status.start.assert_called_once()

    calls = []
    for item in test_items:
        calls.append(call(item))
    mock_status.update.assert_has_calls(calls)

    mock_status.stop.assert_called_once()