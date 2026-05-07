"""Start module of wows-container-log application"""

from PySide6.QtWidgets import QApplication

import sys

from wows_container_log.gui.main_window import MainWindow


def main() -> None:
    """Start the GUI application and run the main event loop.

    This function prepares the main application window and begins processing
    user interactions.

    Args:
        None

    Returns:
        None
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
