"""A strip of colour swatches: click one to select it as the paint colour."""

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QWidget

SWATCH_SIZE = 24


class PaletteWidget(QWidget):
    color_selected = Signal(str)

    def __init__(self, palette: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.palette = palette
        self.selected_index = 0
        self.setFixedSize(SWATCH_SIZE, len(palette) * SWATCH_SIZE)

    def selected_color(self) -> str:
        return self.palette[self.selected_index]

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        for index, color in enumerate(self.palette):
            y = index * SWATCH_SIZE
            painter.fillRect(0, y, SWATCH_SIZE, SWATCH_SIZE, QColor(color))

        y = self.selected_index * SWATCH_SIZE
        painter.setPen(QPen(QColor("white"), 2))
        painter.drawRect(1, y + 1, SWATCH_SIZE - 2, SWATCH_SIZE - 2)
        painter.setPen(QPen(QColor("black"), 2))
        painter.drawRect(0, y, SWATCH_SIZE - 1, SWATCH_SIZE - 1)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        index = int(event.position().y()) // SWATCH_SIZE
        self.selected_index = index
        self.update()
        self.color_selected.emit(self.palette[index])
