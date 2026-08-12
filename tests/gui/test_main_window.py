from PySide6.QtWidgets import QMessageBox

from gui.main_window import MainWindow


def test_window_title(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.windowTitle() == "Alien Editor"


def test_file_menu_actions(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    actions = [a.text() for a in window.file_menu.actions() if not a.isSeparator()]
    assert actions == ["&New...", "&Open...", "E&xit"]


def test_new_action_shows_placeholder_message(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    shown = {}
    monkeypatch.setattr(
        QMessageBox, "information", lambda *args, **kwargs: shown.setdefault("called", True)
    )
    window.new_action.trigger()
    assert shown.get("called") is True


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
