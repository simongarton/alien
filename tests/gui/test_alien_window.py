from PySide6.QtCore import QPoint, Qt

from gui.alien_window import AlienWindow
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
    assert window.centralWidget() is window.pixel_grid


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
