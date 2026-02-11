""" 
This module is the entry point of the application.
"""
from PySide6.QtWidgets import QApplication

from src.gui.main_window import MainWindow

import sys

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
