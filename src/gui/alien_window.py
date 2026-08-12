"""A window for editing a single alien: File > Save / Save As / Close."""

from pathlib import Path

from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QWidget

from .palette_widget import PaletteWidget
from .pixel_grid import PixelGridWidget


class AlienWindow(QMainWindow):
    def __init__(
        self,
        grid: list[list[str]],
        palette: list[str],
        background: str,
        path: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.grid = grid
        self.palette = palette
        self.background = background
        self.path = path
        self.dirty = False

        self.pixel_grid = PixelGridWidget(grid, background=background, selected_color=palette[0])
        self.pixel_grid.cell_changed.connect(self._on_cell_changed)

        self.palette_widget = PaletteWidget(palette)
        self.palette_widget.color_selected.connect(self._on_color_selected)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(self.pixel_grid)
        layout.addWidget(self.palette_widget)
        self.setCentralWidget(container)

        self._update_title()

    def _on_color_selected(self, color: str) -> None:
        self.pixel_grid.selected_color = color

    def _on_cell_changed(self) -> None:
        self.dirty = True
        self._update_title()

    def _update_title(self) -> None:
        name = Path(self.path).name if self.path else "Untitled"
        marker = "*" if self.dirty else ""
        self.setWindowTitle(f"{name}{marker} - Alien Editor")
