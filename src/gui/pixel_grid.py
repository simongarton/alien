"""A read-only view of an alien grid: one filled square per pixel."""

from PySide6.QtGui import QColor, QPainter, QPaintEvent
from PySide6.QtWidgets import QWidget

CELL_SIZE = 20


class PixelGridWidget(QWidget):
    def __init__(self, grid: list[list[str]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.grid = grid
        height = len(grid)
        width = len(grid[0]) if height else 0
        self.setFixedSize(width * CELL_SIZE, height * CELL_SIZE)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        for row_index, row in enumerate(self.grid):
            for col_index, color in enumerate(row):
                painter.fillRect(
                    col_index * CELL_SIZE,
                    row_index * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                    QColor(color),
                )
