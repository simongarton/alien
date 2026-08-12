from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog

from gui.palette_widget import SWATCH_SIZE, PaletteWidget


def _center(index: int) -> QPoint:
    return QPoint(SWATCH_SIZE // 2, index * SWATCH_SIZE + SWATCH_SIZE // 2)


def test_widget_size_matches_palette_length(qtbot):
    palette = ["#FF0000", "#00FF00", "#0000FF"]
    widget = PaletteWidget(palette)
    qtbot.addWidget(widget)
    assert widget.width() == SWATCH_SIZE
    assert widget.height() == 3 * SWATCH_SIZE


def test_first_color_selected_by_default(qtbot):
    palette = ["#FF0000", "#00FF00"]
    widget = PaletteWidget(palette)
    qtbot.addWidget(widget)
    assert widget.selected_index == 0
    assert widget.selected_color() == "#FF0000"


def test_paints_each_swatch_with_its_color(qtbot):
    palette = ["#FF0000", "#00FF00", "#0000FF"]
    widget = PaletteWidget(palette)
    qtbot.addWidget(widget)
    widget.show()
    image = widget.grab().toImage()

    def color_at(index: int) -> str:
        return image.pixelColor(_center(index)).name().upper()

    assert color_at(0) == "#FF0000"
    assert color_at(1) == "#00FF00"
    assert color_at(2) == "#0000FF"


def test_click_selects_swatch_and_emits_signal(qtbot):
    palette = ["#FF0000", "#00FF00", "#0000FF"]
    widget = PaletteWidget(palette)
    qtbot.addWidget(widget)

    with qtbot.waitSignal(widget.color_selected, timeout=1000) as blocker:
        qtbot.mouseClick(widget, Qt.MouseButton.LeftButton, pos=_center(2))

    assert widget.selected_index == 2
    assert widget.selected_color() == "#0000FF"
    assert blocker.args == ["#0000FF"]


def test_double_click_redefines_the_swatch_color(qtbot, monkeypatch):
    palette = ["#FF0000", "#00FF00", "#0000FF"]
    widget = PaletteWidget(palette)
    qtbot.addWidget(widget)
    monkeypatch.setattr(QColorDialog, "getColor", lambda *args, **kwargs: QColor("#ABCDEF"))

    with qtbot.waitSignal(widget.color_selected, timeout=1000) as blocker:
        qtbot.mouseDClick(widget, Qt.MouseButton.LeftButton, pos=_center(1))

    assert widget.palette[1] == "#ABCDEF"
    assert widget.selected_index == 1
    assert blocker.args == ["#ABCDEF"]


def test_double_click_with_invalid_color_leaves_palette_unchanged(qtbot, monkeypatch):
    palette = ["#FF0000", "#00FF00", "#0000FF"]
    widget = PaletteWidget(palette)
    qtbot.addWidget(widget)
    monkeypatch.setattr(QColorDialog, "getColor", lambda *args, **kwargs: QColor())

    qtbot.mouseDClick(widget, Qt.MouseButton.LeftButton, pos=_center(1))

    assert widget.palette == ["#FF0000", "#00FF00", "#0000FF"]


def test_double_click_does_not_change_already_painted_cells(qtbot, monkeypatch):
    from gui.main_window import MainWindow
    from gui.pixel_grid import CELL_SIZE

    grid = [["#FFFFFF"]]
    window = MainWindow()
    qtbot.addWidget(window)
    window._load_alien(grid, ["#FF0000", "#00FF00"], "#FFFFFF")

    center = QPoint(CELL_SIZE // 2, CELL_SIZE // 2)
    qtbot.mouseClick(window.pixel_grid, Qt.MouseButton.LeftButton, pos=center)
    assert window.grid[0][0] == "#FF0000"

    monkeypatch.setattr(QColorDialog, "getColor", lambda *args, **kwargs: QColor("#123456"))
    qtbot.mouseDClick(window.palette_widget, Qt.MouseButton.LeftButton, pos=_center(0))

    assert window.grid[0][0] == "#FF0000"
    assert window.pixel_grid.selected_color == "#123456"
