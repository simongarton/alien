from PySide6.QtCore import QPoint, Qt

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
