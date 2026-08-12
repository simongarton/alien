"""The Alien Editor's single window: File menu with New / Open / Save / Save As / Generate /
Close / Exit, editing one alien at a time."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QWidget,
)

from alien_generator import build_palette, generate_alien

from .alien_io import derive_palette_and_background, load_alien, new_grid, save_alien
from .new_alien_dialog import NewAlienDialog
from .palette_widget import PaletteWidget
from .pixel_grid import PixelGridWidget

OPEN_FILE_FILTER = "Alien files (*.json *.txt)"
SAVE_FILE_FILTER = "JSON files (*.json);;Text files (*.txt)"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.resize(320, 240)
        self.grid: list[list[str]] | None = None
        self.palette: list[str] | None = None
        self.background: str | None = None
        self.path: str | None = None
        self.dirty = False
        self.pixel_grid: PixelGridWidget | None = None
        self.palette_widget: PaletteWidget | None = None

        self._build_menu()
        self._show_placeholder()
        self._update_title()

    def _build_menu(self) -> None:
        self.file_menu = self.menuBar().addMenu("&File")

        self.new_action = QAction("&New...", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self._on_new)
        self.file_menu.addAction(self.new_action)

        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self._on_open)
        self.file_menu.addAction(self.open_action)

        self.file_menu.addSeparator()

        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self._save)
        self.file_menu.addAction(self.save_action)

        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self._save_as)
        self.file_menu.addAction(self.save_as_action)

        self.file_menu.addSeparator()

        self.generate_action = QAction("&Generate", self)
        self.generate_action.setShortcut("Ctrl+G")
        self.generate_action.triggered.connect(self._on_generate)
        self.file_menu.addAction(self.generate_action)

        self.file_menu.addSeparator()

        self.close_action = QAction("&Close", self)
        self.close_action.setShortcut("Ctrl+W")
        self.close_action.triggered.connect(self._on_close)
        self.file_menu.addAction(self.close_action)

        self.file_menu.addSeparator()

        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)

    def _set_alien_actions_enabled(self, enabled: bool) -> None:
        self.save_action.setEnabled(enabled)
        self.save_as_action.setEnabled(enabled)
        self.generate_action.setEnabled(enabled)
        self.close_action.setEnabled(enabled)

    def _show_placeholder(self) -> None:
        self.pixel_grid = None
        self.palette_widget = None
        placeholder = QLabel("No alien open.\nUse File > New or File > Open.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(placeholder)
        self._set_alien_actions_enabled(False)

    def _load_alien(
        self,
        grid: list[list[str]],
        palette: list[str],
        background: str,
        path: str | None = None,
    ) -> None:
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

        self._set_alien_actions_enabled(True)
        self._update_title()

    def _confirm_discard_current(self) -> bool:
        """Return True if it's OK to replace/discard the current alien, prompting to save
        first if it has unsaved changes."""
        if self.grid is None or not self.dirty:
            return True

        reply = QMessageBox.question(
            self,
            "Unsaved changes",
            "Save changes before continuing?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if reply == QMessageBox.StandardButton.Cancel:
            return False
        if reply == QMessageBox.StandardButton.Save:
            return self._save()
        return True

    def _on_new(self) -> None:
        if not self._confirm_discard_current():
            return

        dialog = NewAlienDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        values = dialog.values()
        try:
            palette = build_palette(values["palette"], values["background"])
        except ValueError as exc:
            QMessageBox.warning(self, "New", str(exc))
            return

        grid = new_grid(values["width"], values["height"], values["background"])
        self._load_alien(grid, palette, values["background"])

    def _on_open(self) -> None:
        if not self._confirm_discard_current():
            return

        path, _ = QFileDialog.getOpenFileName(self, "Open Alien", "", OPEN_FILE_FILTER)
        if not path:
            return

        try:
            grid = load_alien(path)
        except (OSError, ValueError, KeyError, IndexError) as exc:
            QMessageBox.warning(self, "Open", f"Could not open {path}:\n{exc}")
            return

        palette, background = derive_palette_and_background(grid)
        self._load_alien(grid, palette, background, path=path)

    def _on_close(self) -> None:
        if not self._confirm_discard_current():
            return

        self.grid = None
        self.palette = None
        self.background = None
        self.path = None
        self.dirty = False
        self._show_placeholder()
        self._update_title()

    def _on_color_selected(self, color: str) -> None:
        self.pixel_grid.selected_color = color

    def _on_cell_changed(self) -> None:
        self.dirty = True
        self._update_title()

    def _has_alien_content(self) -> bool:
        return any(cell != self.background for row in self.grid for cell in row)

    def _on_generate(self) -> None:
        if self._has_alien_content():
            reply = QMessageBox.question(
                self,
                "Generate",
                "This will replace the current alien with a new random one. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        height = len(self.grid)
        width = len(self.grid[0]) if height else 0
        new_grid = generate_alien(
            width=width, height=height, background=self.background, palette=self.palette
        )

        self.grid = new_grid
        self.pixel_grid.grid = new_grid
        self.pixel_grid.update()
        self.dirty = True
        self._update_title()

    def _update_title(self) -> None:
        if self.grid is None:
            self.setWindowTitle("Alien Editor")
            return

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
        if not self._confirm_discard_current():
            event.ignore()
            return

        event.accept()
