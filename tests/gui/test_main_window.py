from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from gui.alien_io import save_alien
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


def test_open_creates_alien_window_from_json_file(qtbot, monkeypatch, tmp_path):
    grid = [["#FFFFFF", "#FF0000"], ["#FFFFFF", "#FFFFFF"]]
    path = tmp_path / "alien.json"
    save_alien(str(path), grid)

    window = MainWindow()
    qtbot.addWidget(window)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwargs: (str(path), ""))

    window.open_action.trigger()

    assert len(window.alien_windows) == 1
    alien_window = window.alien_windows[0]
    assert alien_window.grid == grid
    assert alien_window.path == str(path)
    assert alien_window.background == "#FFFFFF"
    assert alien_window.palette == ["#FF0000"]
    assert "alien.json" in alien_window.windowTitle()
    alien_window.close()


def test_closing_alien_window_removes_it_from_tracking_list(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    monkeypatch.setattr(NewAlienDialog, "exec", lambda self: QDialog.DialogCode.Accepted)
    monkeypatch.setattr(
        NewAlienDialog,
        "values",
        lambda self: {"width": 2, "height": 2, "palette": "cga", "background": "#FFFFFF"},
    )

    window.new_action.trigger()
    assert len(window.alien_windows) == 1
    alien_window = window.alien_windows[0]

    alien_window.close()

    qtbot.waitUntil(lambda: window.alien_windows == [], timeout=1000)


def test_open_does_nothing_when_cancelled(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwargs: ("", ""))

    window.open_action.trigger()

    assert window.alien_windows == []


def test_open_shows_warning_for_invalid_file(qtbot, monkeypatch, tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("not valid json")

    window = MainWindow()
    qtbot.addWidget(window)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwargs: (str(path), ""))
    shown = {}
    monkeypatch.setattr(
        QMessageBox, "warning", lambda *args, **kwargs: shown.setdefault("called", True)
    )

    window.open_action.trigger()

    assert shown.get("called") is True
    assert window.alien_windows == []


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
