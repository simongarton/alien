from gui.pixel_grid import CELL_SIZE, PixelGridWidget


def test_widget_size_matches_grid(qtbot):
    grid = [["#FF0000", "#00FF00", "#0000FF"], ["#FFFFFF", "#000000", "#AAAAAA"]]
    widget = PixelGridWidget(grid)
    qtbot.addWidget(widget)
    assert widget.width() == 3 * CELL_SIZE
    assert widget.height() == 2 * CELL_SIZE


def test_paints_each_cell_with_its_color(qtbot):
    grid = [["#FF0000", "#00FF00"], ["#0000FF", "#FFFFFF"]]
    widget = PixelGridWidget(grid)
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
