from PySide6.QtWidgets import QMainWindow, QTabWidget

from wows_container_log.gui.panels.item_editor_panel import ItemEditorPanel
from wows_container_log import versioning
from wows_container_log.storage import databases


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        databases.init_databases()
        self.setWindowTitle(
            f"WoWS Container Log {versioning.get_version('wows_container_log')}"
        )

        self.setGeometry(100, 100, 1024, 600)

        self._create_main_tab_widget()

    def _create_main_tab_widget(self):
        self.main_tab_widget = QTabWidget()
        self.main_tab_widget.setTabPosition(QTabWidget.TabPosition.West)

        self.main_tab_widget.addTab(ItemEditorPanel(), "Item-Editor")

        self.setCentralWidget(self.main_tab_widget)
