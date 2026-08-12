import json

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox

from gui import alien_window as alien_window_module
from gui.alien_window import AlienWindow
from gui.palette_widget import SWATCH_SIZE, PaletteWidget
from gui.pixel_grid import CELL_SIZE, PixelGridWidget


def test_window_title_for_untitled_alien(qtbot):
    grid = [["#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000"], background="#FFFFFF")
    qtbot.addWidget(window)
    assert window.windowTitle() == "Untitled - Alien Editor"


def test_central_widget_renders_the_given_grid(qtbot):
    grid = [["#FF0000", "#00FF00"]]
    window = AlienWindow(grid=grid, palette=["#FF0000", "#00FF00"], background="#FFFFFF")
    qtbot.addWidget(window)
    assert isinstance(window.pixel_grid, PixelGridWidget)
    assert window.pixel_grid.grid == grid


def test_central_widget_contains_pixel_grid_and_palette(qtbot):
    grid = [["#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000", "#00FF00"], background="#FFFFFF")
    qtbot.addWidget(window)
    assert isinstance(window.palette_widget, PaletteWidget)
    layout = window.centralWidget().layout()
    assert layout.count() == 2
    assert layout.itemAt(0).widget() is window.pixel_grid
    assert layout.itemAt(1).widget() is window.palette_widget


def test_pixel_grid_paints_with_the_first_palette_color(qtbot):
    grid = [["#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000", "#00FF00"], background="#FFFFFF")
    qtbot.addWidget(window)
    assert window.pixel_grid.selected_color == "#FF0000"


def test_clicking_grid_marks_window_dirty_and_updates_title(qtbot):
    grid = [["#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000"], background="#FFFFFF")
    qtbot.addWidget(window)
    assert window.dirty is False

    center = QPoint(CELL_SIZE // 2, CELL_SIZE // 2)
    qtbot.mouseClick(window.pixel_grid, Qt.MouseButton.LeftButton, pos=center)

    assert window.dirty is True
    assert window.windowTitle() == "Untitled* - Alien Editor"
    assert window.grid[0][0] == "#FF0000"


def test_selecting_a_palette_color_updates_the_grids_paint_color(qtbot):
    grid = [["#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000", "#00FF00"], background="#FFFFFF")
    qtbot.addWidget(window)

    second_swatch = QPoint(SWATCH_SIZE // 2, SWATCH_SIZE + SWATCH_SIZE // 2)
    qtbot.mouseClick(window.palette_widget, Qt.MouseButton.LeftButton, pos=second_swatch)

    assert window.pixel_grid.selected_color == "#00FF00"

    center = QPoint(CELL_SIZE // 2, CELL_SIZE // 2)
    qtbot.mouseClick(window.pixel_grid, Qt.MouseButton.LeftButton, pos=center)

    assert window.grid[0][0] == "#00FF00"


def test_file_menu_actions(qtbot):
    grid = [["#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000"], background="#FFFFFF")
    qtbot.addWidget(window)
    actions = [a.text() for a in window.file_menu.actions() if not a.isSeparator()]
    assert actions == ["&Save", "Save &As...", "&Generate", "&Close"]


def test_generate_on_blank_canvas_does_not_prompt(qtbot, monkeypatch):
    grid = [["#FFFFFF", "#FFFFFF"], ["#FFFFFF", "#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000"], background="#FFFFFF")
    qtbot.addWidget(window)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Generate should not prompt when the canvas is blank")

    monkeypatch.setattr(QMessageBox, "question", fail_if_called)
    monkeypatch.setattr(
        alien_window_module,
        "generate_alien",
        lambda **kwargs: [["#FF0000", "#FFFFFF"], ["#FFFFFF", "#FF0000"]],
    )

    window.generate_action.trigger()

    assert window.grid == [["#FF0000", "#FFFFFF"], ["#FFFFFF", "#FF0000"]]
    assert window.pixel_grid.grid is window.grid
    assert window.dirty is True


def test_generate_with_existing_content_prompts_and_confirms(qtbot, monkeypatch):
    grid = [["#FF0000", "#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000"], background="#FFFFFF")
    qtbot.addWidget(window)

    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Yes
    )
    monkeypatch.setattr(
        alien_window_module, "generate_alien", lambda **kwargs: [["#00FF00", "#00FF00"]]
    )

    window.generate_action.trigger()

    assert window.grid == [["#00FF00", "#00FF00"]]
    assert window.dirty is True


def test_generate_with_existing_content_cancelled_leaves_grid_unchanged(qtbot, monkeypatch):
    grid = [["#FF0000", "#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000"], background="#FFFFFF")
    qtbot.addWidget(window)

    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.No
    )
    called = {}

    def fail_if_called(**kwargs):
        called["was_called"] = True
        return [["#00FF00", "#00FF00"]]

    monkeypatch.setattr(alien_window_module, "generate_alien", fail_if_called)

    window.generate_action.trigger()

    assert "was_called" not in called
    assert window.grid == grid
    assert window.dirty is False


def test_generate_uses_current_dimensions_background_and_palette(qtbot, monkeypatch):
    grid = [["#FFFFFF", "#FFFFFF", "#FFFFFF"], ["#FFFFFF", "#FFFFFF", "#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000", "#00FF00"], background="#FFFFFF")
    qtbot.addWidget(window)

    captured = {}

    def fake_generate_alien(**kwargs):
        captured.update(kwargs)
        return [["#123456"] * 3, ["#123456"] * 3]

    monkeypatch.setattr(alien_window_module, "generate_alien", fake_generate_alien)

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
    window = AlienWindow(grid=grid, palette=["#FF0000"], background="#FFFFFF", path=str(path))
    qtbot.addWidget(window)
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
    grid = [["#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000"], background="#FFFFFF")
    qtbot.addWidget(window)
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
    grid = [["#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000"], background="#FFFFFF")
    qtbot.addWidget(window)
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (path_without_extension, "Text files (*.txt)"),
    )

    window.save_as_action.trigger()

    assert window.path == path_without_extension + ".txt"
    assert (tmp_path / "alien.txt").exists()


def test_save_as_cancelled_leaves_window_unchanged(qtbot, monkeypatch):
    grid = [["#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000"], background="#FFFFFF")
    qtbot.addWidget(window)
    window.dirty = True
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: ("", ""))

    window.save_as_action.trigger()

    assert window.path is None
    assert window.dirty is True


def test_close_without_unsaved_changes_closes_immediately(qtbot):
    grid = [["#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000"], background="#FFFFFF")
    qtbot.addWidget(window)
    window.show()

    window.close()

    assert not window.isVisible()


def test_close_with_unsaved_changes_prompts_and_cancel_keeps_open(qtbot, monkeypatch):
    grid = [["#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000"], background="#FFFFFF")
    qtbot.addWidget(window)
    window.show()
    window.dirty = True
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Cancel
    )

    window.close()

    assert window.isVisible()


def test_close_with_unsaved_changes_discard_closes_without_saving(qtbot, monkeypatch, tmp_path):
    path = tmp_path / "alien.json"
    grid = [["#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000"], background="#FFFFFF", path=str(path))
    qtbot.addWidget(window)
    window.show()
    window.dirty = True
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Discard
    )

    window.close()

    assert not window.isVisible()
    assert not path.exists()


def test_close_with_unsaved_changes_save_writes_file_then_closes(qtbot, monkeypatch, tmp_path):
    path = tmp_path / "alien.json"
    grid = [["#FFFFFF"]]
    window = AlienWindow(grid=grid, palette=["#FF0000"], background="#FFFFFF", path=str(path))
    qtbot.addWidget(window)
    window.show()
    window.dirty = True
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Save
    )

    window.close()

    assert not window.isVisible()
    assert path.exists()
