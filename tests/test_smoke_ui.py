import pytest

pytest.importorskip("PySide6")

from PySide6 import QtCore

from coinbara.window import CoinFlipWindow


@pytest.mark.smoke
def test_window_starts_and_flip_completes(qtbot) -> None:
    window = CoinFlipWindow()
    qtbot.addWidget(window)
    window.show()

    qtbot.mouseClick(window.flip_button, QtCore.Qt.LeftButton)
    qtbot.waitUntil(lambda: window.engine.is_flipping is False, timeout=2500)

    assert window.result_label.text() in {"Heads", "Tails"}
    assert window.flip_button.isEnabled()
