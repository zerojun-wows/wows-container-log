from PySide6.QtWidgets import QApplication

import sys

from wows_container_log.gui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
