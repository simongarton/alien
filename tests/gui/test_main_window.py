import json

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from gui import main_window as main_window_module
from gui.alien_io import save_alien
from gui.main_window import MainWindow
from gui.new_alien_dialog import NewAlienDialog
from gui.palette_widget import SWATCH_SIZE, PaletteWidget
from gui.pixel_grid import CELL_SIZE, PixelGridWidget


def _accept_new(monkeypatch, width=4, height=3, palette="cga", background="#FFFFFF"):
    monkeypatch.setattr(NewAlienDialog, "exec", lambda self: QDialog.DialogCode.Accepted)
    monkeypatch.setattr(
        NewAlienDialog,
        "values",
        lambda self: {
            "width": width,
            "height": height,
            "palette": palette,
            "background": background,
        },
    )


def test_window_title_initial(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.windowTitle() == "Alien Editor"
    assert window.pixel_grid is None


def test_file_menu_actions(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    actions = [a.text() for a in window.file_menu.actions() if not a.isSeparator()]
    assert actions == [
        "&New...",
        "&Open...",
        "&Save",
        "Save &As...",
        "&Generate",
        "&Close",
        "E&xit",
    ]


def test_alien_actions_disabled_initially(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert not window.save_action.isEnabled()
    assert not window.save_as_action.isEnabled()
    assert not window.generate_action.isEnabled()
    assert not window.close_action.isEnabled()


def test_new_loads_alien_into_window_when_accepted(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    _accept_new(monkeypatch, width=4, height=3)

    window.new_action.trigger()

    assert len(window.grid) == 3
    assert len(window.grid[0]) == 4
    assert isinstance(window.pixel_grid, PixelGridWidget)
    assert window.save_action.isEnabled()
    assert window.close_action.isEnabled()
    assert window.windowTitle() == "Untitled - Alien Editor"


def test_new_does_nothing_when_cancelled(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    monkeypatch.setattr(NewAlienDialog, "exec", lambda self: QDialog.DialogCode.Rejected)

    window.new_action.trigger()

    assert window.grid is None


def test_open_loads_alien_from_json_file(qtbot, monkeypatch, tmp_path):
    grid = [["#FFFFFF", "#FF0000"], ["#FFFFFF", "#FFFFFF"]]
    path = tmp_path / "alien.json"
    save_alien(str(path), grid)

    window = MainWindow()
    qtbot.addWidget(window)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwargs: (str(path), ""))

    window.open_action.trigger()

    assert window.grid == grid
    assert window.path == str(path)
    assert window.background == "#FFFFFF"
    assert window.palette == ["#FF0000"]
    assert "alien.json" in window.windowTitle()


def test_open_does_nothing_when_cancelled(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwargs: ("", ""))

    window.open_action.trigger()

    assert window.grid is None


def test_open_shows_warning_for_invalid_file(qtbot, monkeypatch, tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("not valid json")

    window = MainWindow()
    qtbot.addWidget(window)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwargs: (str(path), ""))
    shown = {}
    monkeypatch.setattr(
        QMessageBox, "warning", lambda *args, **kwargs: shown.setdefault("called", True)
    )

    window.open_action.trigger()

    assert shown.get("called") is True
    assert window.grid is None


def test_central_widget_contains_pixel_grid_and_palette(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    _accept_new(monkeypatch, width=1, height=1)

    window.new_action.trigger()

    assert isinstance(window.palette_widget, PaletteWidget)
    layout = window.centralWidget().layout()
    assert layout.count() == 2
    assert layout.itemAt(0).widget() is window.pixel_grid
    assert layout.itemAt(1).widget() is window.palette_widget


def test_pixel_grid_paints_with_the_first_palette_color(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien([["#FFFFFF"]], ["#FF0000", "#00FF00"], "#FFFFFF")

    assert window.pixel_grid.selected_color == "#FF0000"


def test_clicking_grid_marks_window_dirty_and_updates_title(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien([["#FFFFFF"]], ["#FF0000"], "#FFFFFF")
    assert window.dirty is False

    center = QPoint(CELL_SIZE // 2, CELL_SIZE // 2)
    qtbot.mouseClick(window.pixel_grid, Qt.MouseButton.LeftButton, pos=center)

    assert window.dirty is True
    assert window.windowTitle() == "Untitled* - Alien Editor"
    assert window.grid[0][0] == "#FF0000"


def test_selecting_a_palette_color_updates_the_grids_paint_color(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien([["#FFFFFF"]], ["#FF0000", "#00FF00"], "#FFFFFF")

    second_swatch = QPoint(SWATCH_SIZE // 2, SWATCH_SIZE + SWATCH_SIZE // 2)
    qtbot.mouseClick(window.palette_widget, Qt.MouseButton.LeftButton, pos=second_swatch)

    assert window.pixel_grid.selected_color == "#00FF00"

    center = QPoint(CELL_SIZE // 2, CELL_SIZE // 2)
    qtbot.mouseClick(window.pixel_grid, Qt.MouseButton.LeftButton, pos=center)

    assert window.grid[0][0] == "#00FF00"


def test_generate_on_blank_canvas_does_not_prompt(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien(
        [["#FFFFFF", "#FFFFFF"], ["#FFFFFF", "#FFFFFF"]], ["#FF0000"], "#FFFFFF"
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Generate should not prompt when the canvas is blank")

    monkeypatch.setattr(QMessageBox, "question", fail_if_called)
    monkeypatch.setattr(
        main_window_module,
        "generate_alien",
        lambda **kwargs: [["#FF0000", "#FFFFFF"], ["#FFFFFF", "#FF0000"]],
    )

    window.generate_action.trigger()

    assert window.grid == [["#FF0000", "#FFFFFF"], ["#FFFFFF", "#FF0000"]]
    assert window.pixel_grid.grid is window.grid
    assert window.dirty is True


def test_generate_with_existing_content_prompts_and_confirms(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien([["#FF0000", "#FFFFFF"]], ["#FF0000"], "#FFFFFF")

    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Yes
    )
    monkeypatch.setattr(
        main_window_module, "generate_alien", lambda **kwargs: [["#00FF00", "#00FF00"]]
    )

    window.generate_action.trigger()

    assert window.grid == [["#00FF00", "#00FF00"]]
    assert window.dirty is True


def test_generate_with_existing_content_cancelled_leaves_grid_unchanged(qtbot, monkeypatch):
    grid = [["#FF0000", "#FFFFFF"]]
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien(grid, ["#FF0000"], "#FFFFFF")

    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.No
    )
    called = {}

    def fail_if_called(**kwargs):
        called["was_called"] = True
        return [["#00FF00", "#00FF00"]]

    monkeypatch.setattr(main_window_module, "generate_alien", fail_if_called)

    window.generate_action.trigger()

    assert "was_called" not in called
    assert window.grid == grid
    assert window.dirty is False


def test_generate_uses_current_dimensions_background_and_palette(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien(
        [["#FFFFFF", "#FFFFFF", "#FFFFFF"], ["#FFFFFF", "#FFFFFF", "#FFFFFF"]],
        ["#FF0000", "#00FF00"],
        "#FFFFFF",
    )

    captured = {}

    def fake_generate_alien(**kwargs):
        captured.update(kwargs)
        return [["#123456"] * 3, ["#123456"] * 3]

    monkeypatch.setattr(main_window_module, "generate_alien", fake_generate_alien)

    window.generate_action.trigger()

    assert captured == {
        "width": 3,
        "height": 2,
        "background": "#FFFFFF",
        "palette": ["#FF0000", "#00FF00"],
    }


def test_save_with_existing_path_writes_file_without_prompting(qtbot, monkeypatch, tmp_path):
    path = tmp_path / "alien.json"
    grid = [["#FFFFFF"]]
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien(grid, ["#FF0000"], "#FFFFFF", path=str(path))
    window.dirty = True
    window._update_title()

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Save As dialog should not be shown when a path already exists")

    monkeypatch.setattr(QFileDialog, "getSaveFileName", fail_if_called)

    window.save_action.trigger()

    assert window.dirty is False
    assert window.windowTitle() == "alien.json - Alien Editor"
    with open(path) as f:
        assert json.load(f) == grid


def test_save_without_path_behaves_like_save_as(qtbot, monkeypatch, tmp_path):
    path = tmp_path / "new_alien.json"
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien([["#FFFFFF"]], ["#FF0000"], "#FFFFFF")
    window.dirty = True
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", lambda *args, **kwargs: (str(path), "JSON files (*.json)")
    )

    window.save_action.trigger()

    assert window.path == str(path)
    assert window.dirty is False
    assert path.exists()


def test_save_as_appends_extension_from_selected_filter(qtbot, monkeypatch, tmp_path):
    path_without_extension = str(tmp_path / "alien")
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien([["#FFFFFF"]], ["#FF0000"], "#FFFFFF")
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (path_without_extension, "Text files (*.txt)"),
    )

    window.save_as_action.trigger()

    assert window.path == path_without_extension + ".txt"
    assert (tmp_path / "alien.txt").exists()


def test_save_as_cancelled_leaves_window_unchanged(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien([["#FFFFFF"]], ["#FF0000"], "#FFFFFF")
    window.dirty = True
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: ("", ""))

    window.save_as_action.trigger()

    assert window.path is None
    assert window.dirty is True


def test_close_action_without_unsaved_changes_clears_alien_immediately(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien([["#FFFFFF"]], ["#FF0000"], "#FFFFFF")

    window.close_action.trigger()

    assert window.grid is None
    assert window.pixel_grid is None
    assert window.windowTitle() == "Alien Editor"
    assert not window.save_action.isEnabled()


def test_close_action_with_unsaved_changes_prompts_and_cancel_keeps_alien(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien([["#FFFFFF"]], ["#FF0000"], "#FFFFFF")
    window.dirty = True
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Cancel
    )

    window.close_action.trigger()

    assert window.grid is not None


def test_close_action_with_unsaved_changes_discard_clears_alien(qtbot, monkeypatch, tmp_path):
    path = tmp_path / "alien.json"
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien([["#FFFFFF"]], ["#FF0000"], "#FFFFFF", path=str(path))
    window.dirty = True
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Discard
    )

    window.close_action.trigger()

    assert window.grid is None
    assert not path.exists()


def test_new_prompts_when_current_alien_dirty_and_cancel_aborts(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    original_grid = [["#FFFFFF"]]
    window._load_alien(original_grid, ["#FF0000"], "#FFFFFF")
    window.dirty = True
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Cancel
    )
    _accept_new(monkeypatch, width=5, height=5)

    window.new_action.trigger()

    assert window.grid is original_grid


def test_open_prompts_when_current_alien_dirty_and_save_writes_before_opening(
    qtbot, monkeypatch, tmp_path
):
    old_path = tmp_path / "old.json"
    new_grid = [["#FFFFFF", "#00FF00"], ["#FFFFFF", "#FFFFFF"]]
    new_path = tmp_path / "new.json"
    save_alien(str(new_path), new_grid)

    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien([["#FFFFFF"]], ["#FF0000"], "#FFFFFF", path=str(old_path))
    window.dirty = True
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Save
    )
    monkeypatch.setattr(
        QFileDialog, "getOpenFileName", lambda *args, **kwargs: (str(new_path), "")
    )

    window.open_action.trigger()

    assert old_path.exists()
    assert window.grid == new_grid
    assert window.path == str(new_path)


def test_window_close_without_unsaved_changes_closes_immediately(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    window.close()

    assert not window.isVisible()


def test_window_close_with_unsaved_changes_prompts_and_cancel_keeps_open(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien([["#FFFFFF"]], ["#FF0000"], "#FFFFFF")
    window.show()
    window.dirty = True
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Cancel
    )

    window.close()

    assert window.isVisible()


def test_window_close_with_unsaved_changes_discard_closes_without_saving(
    qtbot, monkeypatch, tmp_path
):
    path = tmp_path / "alien.json"
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien([["#FFFFFF"]], ["#FF0000"], "#FFFFFF", path=str(path))
    window.show()
    window.dirty = True
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Discard
    )

    window.close()

    assert not window.isVisible()
    assert not path.exists()


def test_window_close_with_unsaved_changes_save_writes_file_then_closes(
    qtbot, monkeypatch, tmp_path
):
    path = tmp_path / "alien.json"
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien([["#FFFFFF"]], ["#FF0000"], "#FFFFFF", path=str(path))
    window.show()
    window.dirty = True
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Save
    )

    window.close()

    assert not window.isVisible()
    assert path.exists()
