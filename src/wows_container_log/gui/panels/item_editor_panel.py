from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QHeaderView,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QLabel,
    QTableView,
    QPushButton,
)

from wows_container_log.storage import item_repo


class ItemEditorPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        main_layout = QVBoxLayout(self)

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Horizontal)  # pyright: ignore[reportAttributeAccessIssue]

        splitter.addWidget(self._create_reward_items_left_widget(splitter))

        # ----- Rechter Bereich: Placeholder für Entries -----
        right_placeholder = QLabel("Drop-Entries (später)")
        right_placeholder.setAlignment(Qt.AlignCenter)  # pyright: ignore[reportAttributeAccessIssue]
        splitter.addWidget(right_placeholder)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)

        # Initial: Buttons, die eine Auswahl brauchen, deaktivieren
        self.btn_duplicate_item.setEnabled(False)
        self.btn_edit_item.setEnabled(False)
        self.btn_delete_item.setEnabled(False)

        self.reload_reward_items_table_view()
        # TODO: hier später Signal/Slot-Verbindungen ergänzen
        # z.B. self.btn_new_item.clicked.connect(self.on_new_item_clicked)

    def _create_reward_items_left_widget(self, splitter: QSplitter) -> QWidget:
        left_widget = QWidget(splitter)
        left_layout = QVBoxLayout(left_widget)

        title_label = QLabel("Belohnungs-Items")
        left_layout.addWidget(title_label)

        left_layout.addWidget(self._create_reward_items_table_view(left_widget))

        left_layout.addLayout(self._create_reward_items_button_row_layout())

        return left_widget

    def _create_reward_items_table_view(self, widget: QWidget) -> QWidget:
        self.reward_items_table_view = QTableView(widget)
        self.reward_items_table_view_model = QStandardItemModel(self)

        # Spalten definieren
        self.reward_items_table_view_model.setHorizontalHeaderLabels(
            ["ID", "Name", "Menge", "Metadaten", "Nur einmal droppbar"]
        )
        self.reward_items_table_view.setModel(self.reward_items_table_view_model)

        # Bearbeitung in der View deaktivieren (zusätzlich Flags später im Model möglich)
        self.reward_items_table_view.setEditTriggers(QTableView.NoEditTriggers)  # pyright: ignore[reportAttributeAccessIssue]

        return self.reward_items_table_view

    def _create_reward_items_button_row_layout(self) -> QHBoxLayout:
        button_row = QHBoxLayout()

        self.btn_new_item = QPushButton("Neu")
        self.btn_duplicate_item = QPushButton("Duplizieren")
        self.btn_edit_item = QPushButton("Bearbeiten")
        self.btn_delete_item = QPushButton("Löschen")

        button_row.addWidget(self.btn_new_item)
        button_row.addWidget(self.btn_duplicate_item)
        button_row.addWidget(self.btn_edit_item)
        button_row.addWidget(self.btn_delete_item)
        button_row.addStretch()

        return button_row

    # -----------------------------------------------------------------
    # Code for data relevant actions of visual widgets
    # -----------------------------------------------------------------

    def reload_reward_items_table_view(self) -> None:
        self.reward_items_table_view_model.clear()
        self.reward_items_table_view_model.setHorizontalHeaderLabels(
            ["ID", "Name", "Menge", "Metadaten", "Nur einmal droppbar"]
        )
        header = self.reward_items_table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents) # pyright: ignore[reportAttributeAccessIssue]

        item_list = item_repo.get_all_items()

        if not item_list:
            row = [QStandardItem("Keine Items vorhanden")]
            # restliche Spalten leer auffüllen
            row += [QStandardItem("") for _ in range(4)]
            for item in row:
                item.setEditable(False)
            self.reward_items_table_view_model.appendRow(row)
            return

        for reward_item in item_list:
            row = [
                QStandardItem(str(reward_item.id)),
                QStandardItem(reward_item.name),
                QStandardItem(str(reward_item.amount)),
                QStandardItem(reward_item.meta or ""),
                QStandardItem("Ja" if reward_item.unique_once else "Nein"),
            ]
            for item in row:
                item.setEditable(False)
            self.reward_items_table_view_model.appendRow(row)
