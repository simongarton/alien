from PySide6.QtCore import QPoint, Qt

from gui.pixel_grid import CELL_SIZE, PixelGridWidget


def _center(row: int, col: int) -> QPoint:
    return QPoint(col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2)


def test_widget_size_matches_grid(qtbot):
    grid = [["#FF0000", "#00FF00", "#0000FF"], ["#FFFFFF", "#000000", "#AAAAAA"]]
    widget = PixelGridWidget(grid, background="#FFFFFF", selected_color="#FF0000")
    qtbot.addWidget(widget)
    assert widget.width() == 3 * CELL_SIZE
    assert widget.height() == 2 * CELL_SIZE


def test_paints_each_cell_with_its_color(qtbot):
    grid = [["#FF0000", "#00FF00"], ["#0000FF", "#FFFFFF"]]
    widget = PixelGridWidget(grid, background="#FFFFFF", selected_color="#000000")
    qtbot.addWidget(widget)
    widget.show()
    image = widget.grab().toImage()

    def color_at(row: int, col: int) -> str:
        x = col * CELL_SIZE + CELL_SIZE // 2
        y = row * CELL_SIZE + CELL_SIZE // 2
        return image.pixelColor(x, y).name().upper()

    assert color_at(0, 0) == "#FF0000"
    assert color_at(0, 1) == "#00FF00"
    assert color_at(1, 0) == "#0000FF"
    assert color_at(1, 1) == "#FFFFFF"


def test_click_paints_the_selected_color(qtbot):
    grid = [["#FFFFFF", "#FFFFFF"], ["#FFFFFF", "#FFFFFF"]]
    widget = PixelGridWidget(grid, background="#FFFFFF", selected_color="#FF0000")
    qtbot.addWidget(widget)

    qtbot.mouseClick(widget, Qt.MouseButton.LeftButton, pos=_center(0, 1))

    assert widget.grid[0][1] == "#FF0000"
    assert widget.grid[0][0] == "#FFFFFF"


def test_clicking_a_painted_cell_again_toggles_back_to_background(qtbot):
    grid = [["#FFFFFF"]]
    widget = PixelGridWidget(grid, background="#FFFFFF", selected_color="#FF0000")
    qtbot.addWidget(widget)

    qtbot.mouseClick(widget, Qt.MouseButton.LeftButton, pos=_center(0, 0))
    assert widget.grid[0][0] == "#FF0000"

    qtbot.mouseClick(widget, Qt.MouseButton.LeftButton, pos=_center(0, 0))
    assert widget.grid[0][0] == "#FFFFFF"


def test_click_emits_cell_changed_signal(qtbot):
    grid = [["#FFFFFF"]]
    widget = PixelGridWidget(grid, background="#FFFFFF", selected_color="#FF0000")
    qtbot.addWidget(widget)

    with qtbot.waitSignal(widget.cell_changed, timeout=1000):
        qtbot.mouseClick(widget, Qt.MouseButton.LeftButton, pos=_center(0, 0))
