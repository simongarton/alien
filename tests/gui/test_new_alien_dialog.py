from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog

from gui.new_alien_dialog import NewAlienDialog


def test_default_values(qtbot):
    dialog = NewAlienDialog()
    qtbot.addWidget(dialog)
    values = dialog.values()
    assert values == {
        "width": 16,
        "height": 16,
        "palette": "cga",
        "background": "#FFFFFF",
    }


def test_palette_choices(qtbot):
    dialog = NewAlienDialog()
    qtbot.addWidget(dialog)
    items = [dialog.palette_combo.itemText(i) for i in range(dialog.palette_combo.count())]
    assert items == ["cga", "green", "red", "blue", "full"]


def test_changing_fields_updates_values(qtbot):
    dialog = NewAlienDialog()
    qtbot.addWidget(dialog)
    dialog.width_spin.setValue(32)
    dialog.height_spin.setValue(8)
    dialog.palette_combo.setCurrentText("green")

    values = dialog.values()

    assert values["width"] == 32
    assert values["height"] == 8
    assert values["palette"] == "green"


def test_background_button_opens_color_dialog(qtbot, monkeypatch):
    dialog = NewAlienDialog()
    qtbot.addWidget(dialog)
    monkeypatch.setattr(QColorDialog, "getColor", lambda *args, **kwargs: QColor("#112233"))

    dialog.background_button.click()

    assert dialog.values()["background"] == "#112233"


def test_background_button_ignores_invalid_color(qtbot, monkeypatch):
    dialog = NewAlienDialog()
    qtbot.addWidget(dialog)
    monkeypatch.setattr(QColorDialog, "getColor", lambda *args, **kwargs: QColor())

    dialog.background_button.click()

    assert dialog.values()["background"] == "#FFFFFF"
