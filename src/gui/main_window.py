"""Main application window: File menu with New / Open / Exit."""

from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import QDialog, QMainWindow, QMessageBox

from alien_generator import build_palette

from .alien_io import new_grid
from .alien_window import AlienWindow
from .new_alien_dialog import NewAlienDialog


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Alien Editor")
        self.resize(320, 240)
        self.alien_windows: list[AlienWindow] = []
        self._build_menu()

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

        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)

    def _on_new(self) -> None:
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
        window = AlienWindow(grid=grid, palette=palette, background=values["background"])
        self.alien_windows.append(window)
        window.show()

    def _on_open(self) -> None:
        QMessageBox.information(self, "Open", "Not implemented yet.")

    def closeEvent(self, event: QCloseEvent) -> None:
        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
