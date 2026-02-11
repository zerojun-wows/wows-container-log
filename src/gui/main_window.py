"""
This module contains the main window of the application.
"""
from PySide6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    """
    This class is the main window of the application.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("World Of Warships Container Log")
        self.setGeometry(100, 100, 800, 600)
        self.show()
