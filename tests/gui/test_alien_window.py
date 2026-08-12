from gui.alien_window import AlienWindow
from gui.pixel_grid import PixelGridWidget


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
