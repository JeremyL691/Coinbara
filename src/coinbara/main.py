from __future__ import annotations

import sys
import traceback

from PySide6 import QtCore, QtGui, QtWidgets

from .assets import asset_path
from .window import CoinFlipWindow


def main() -> None:
    try:
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("Coinbara")
        app.setOrganizationName("Vibecoding Projects")

        icon_path = asset_path("app_icon.ico")
        if icon_path.exists():
            app.setWindowIcon(QtGui.QIcon(str(icon_path)))

        window = CoinFlipWindow()
        window.show()
        sys.exit(app.exec())
    except Exception:
        err = traceback.format_exc()
        QtWidgets.QMessageBox.critical(None, "Coinbara failed", err)
        raise


if __name__ == "__main__":
    main()
