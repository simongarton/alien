"""A window for editing a single alien: File > Save / Save As / Close."""

from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QWidget

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

        self.pixel_grid = PixelGridWidget(grid)
        self.setCentralWidget(self.pixel_grid)

        self._update_title()

    def _update_title(self) -> None:
        name = Path(self.path).name if self.path else "Untitled"
        marker = "*" if self.dirty else ""
        self.setWindowTitle(f"{name}{marker} - Alien Editor")
