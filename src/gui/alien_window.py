"""A window for editing a single alien: File > Save / Save As / Close."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QWidget,
)

from .alien_io import save_alien
from .palette_widget import PaletteWidget
from .pixel_grid import PixelGridWidget

SAVE_FILE_FILTER = "JSON files (*.json);;Text files (*.txt)"


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
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
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

        self._build_menu()
        self._update_title()

    def _build_menu(self) -> None:
        self.file_menu = self.menuBar().addMenu("&File")

        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self._save)
        self.file_menu.addAction(self.save_action)

        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self._save_as)
        self.file_menu.addAction(self.save_as_action)

        self.file_menu.addSeparator()

        self.close_action = QAction("&Close", self)
        self.close_action.setShortcut("Ctrl+W")
        self.close_action.triggered.connect(self.close)
        self.file_menu.addAction(self.close_action)

    def _on_color_selected(self, color: str) -> None:
        self.pixel_grid.selected_color = color

    def _on_cell_changed(self) -> None:
        self.dirty = True
        self._update_title()

    def _update_title(self) -> None:
        name = Path(self.path).name if self.path else "Untitled"
        marker = "*" if self.dirty else ""
        self.setWindowTitle(f"{name}{marker} - Alien Editor")

    def _save(self) -> bool:
        if self.path is None:
            return self._save_as()

        save_alien(self.path, self.grid)
        self.dirty = False
        self._update_title()
        return True

    def _save_as(self) -> bool:
        filename, selected_filter = QFileDialog.getSaveFileName(
            self, "Save Alien As", self.path or "", SAVE_FILE_FILTER
        )
        if not filename:
            return False

        if not filename.lower().endswith((".json", ".txt")):
            filename += ".json" if "json" in selected_filter.lower() else ".txt"

        self.path = filename
        save_alien(self.path, self.grid)
        self.dirty = False
        self._update_title()
        return True

    def closeEvent(self, event: QCloseEvent) -> None:
        if not self.dirty:
            event.accept()
            return

        reply = QMessageBox.question(
            self,
            "Unsaved changes",
            "Save changes before closing?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if reply == QMessageBox.StandardButton.Cancel:
            event.ignore()
            return
        if reply == QMessageBox.StandardButton.Save and not self._save():
            event.ignore()
            return
        event.accept()
