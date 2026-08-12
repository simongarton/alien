"""Dialog for the File > New action: width, height, palette, background."""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from alien_generator import SHADE_PALETTES

PALETTE_NAMES = ["cga", *SHADE_PALETTES.keys(), "full"]
DEFAULT_BACKGROUND = "#FFFFFF"


class ColorButton(QPushButton):
    """A button showing the current colour as its background; click to change it."""

    def __init__(self, color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = color
        self.setFixedWidth(60)
        self._update_style()
        self.clicked.connect(self._choose_color)

    def _update_style(self) -> None:
        self.setStyleSheet(f"background-color: {self._color};")

    def _choose_color(self) -> None:
        chosen = QColorDialog.getColor(QColor(self._color), self, "Choose colour")
        if chosen.isValid():
            self._color = chosen.name().upper()
            self._update_style()

    def color(self) -> str:
        return self._color


class NewAlienDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Alien")

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 64)
        self.width_spin.setValue(16)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 64)
        self.height_spin.setValue(16)

        self.palette_combo = QComboBox()
        self.palette_combo.addItems(PALETTE_NAMES)

        self.background_button = ColorButton(DEFAULT_BACKGROUND)

        form = QFormLayout()
        form.addRow("Width:", self.width_spin)
        form.addRow("Height:", self.height_spin)
        form.addRow("Palette:", self.palette_combo)
        form.addRow("Background:", self.background_button)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self) -> dict:
        return {
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "palette": self.palette_combo.currentText(),
            "background": self.background_button.color(),
        }
