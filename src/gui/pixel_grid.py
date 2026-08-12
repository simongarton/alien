"""A clickable grid of alien pixels: click a cell to paint it, click again to erase."""

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPaintEvent
from PySide6.QtWidgets import QWidget

CELL_SIZE = 20


class PixelGridWidget(QWidget):
    cell_changed = Signal()

    def __init__(
        self,
        grid: list[list[str]],
        background: str,
        selected_color: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.grid = grid
        self.background = background
        self.selected_color = selected_color
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

    def mousePressEvent(self, event: QMouseEvent) -> None:
        col = int(event.position().x()) // CELL_SIZE
        row = int(event.position().y()) // CELL_SIZE

        if self.grid[row][col] == self.selected_color:
            self.grid[row][col] = self.background
        else:
            self.grid[row][col] = self.selected_color

        self.update()
        self.cell_changed.emit()
