from PySide6.QtWidgets import QDialog, QMessageBox

from gui.alien_window import AlienWindow
from gui.main_window import MainWindow
from gui.new_alien_dialog import NewAlienDialog


def test_window_title(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.windowTitle() == "Alien Editor"


def test_file_menu_actions(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    actions = [a.text() for a in window.file_menu.actions() if not a.isSeparator()]
    assert actions == ["&New...", "&Open...", "E&xit"]


def test_new_creates_alien_window_when_accepted(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    monkeypatch.setattr(NewAlienDialog, "exec", lambda self: QDialog.DialogCode.Accepted)
    monkeypatch.setattr(
        NewAlienDialog,
        "values",
        lambda self: {"width": 4, "height": 3, "palette": "cga", "background": "#FFFFFF"},
    )

    window.new_action.trigger()

    assert len(window.alien_windows) == 1
    alien_window = window.alien_windows[0]
    assert isinstance(alien_window, AlienWindow)
    assert len(alien_window.pixel_grid.grid) == 3
    assert len(alien_window.pixel_grid.grid[0]) == 4
    alien_window.close()


def test_new_does_nothing_when_cancelled(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    monkeypatch.setattr(NewAlienDialog, "exec", lambda self: QDialog.DialogCode.Rejected)

    window.new_action.trigger()

    assert window.alien_windows == []


def test_open_action_shows_placeholder_message(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    shown = {}
    monkeypatch.setattr(
        QMessageBox, "information", lambda *args, **kwargs: shown.setdefault("called", True)
    )
    window.open_action.trigger()
    assert shown.get("called") is True


def test_close_confirmed_accepts(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Yes
    )
    window.close()
    assert not window.isVisible()


def test_close_cancelled_keeps_window_open(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.No
    )
    window.close()
    assert window.isVisible()
