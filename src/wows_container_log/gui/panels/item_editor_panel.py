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

from wows_container_log.gui.dialogs.reward_item import RewardItemDialog
from wows_container_log.models.container import RewardItem
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
        self.duplicate_reward_item_button.setEnabled(False)
        self.edit_reward_item_button.setEnabled(False)
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

        self.reward_items_table_view_model.setHorizontalHeaderLabels(
            ["ID", "Name", "Menge", "Metadaten", "Nur einmal droppbar"]
        )
        self.reward_items_table_view.setModel(self.reward_items_table_view_model)
        self.reward_items_table_view.setSelectionBehavior(QTableView.SelectRows)  # pyright: ignore[reportAttributeAccessIssue]
        self.reward_items_table_view.setSelectionMode(QTableView.SingleSelection)  # pyright: ignore[reportAttributeAccessIssue]
        self.reward_items_table_view.selectionModel().selectionChanged.connect(
            self._on_reward_items_table_view_selection_changed
        )
        # Bearbeitung in der View deaktivieren (zusätzlich Flags später im Model möglich)
        self.reward_items_table_view.setEditTriggers(QTableView.NoEditTriggers)  # pyright: ignore[reportAttributeAccessIssue]

        return self.reward_items_table_view

    def _create_reward_items_button_row_layout(self) -> QHBoxLayout:
        button_row = QHBoxLayout()

        self.new_reward_item_button = QPushButton("Neu")
        self.new_reward_item_button.clicked.connect(
            self.on_new_reward_item_button_clicked
        )
        self.edit_reward_item_button = QPushButton("Bearbeiten")
        self.edit_reward_item_button.clicked.connect(
            self.on_edit_reward_item_button_clicked
        )
        self.duplicate_reward_item_button = QPushButton("Duplizieren")
        self.duplicate_reward_item_button.clicked.connect(
            self.on_duplicate_reward_item_button_clicked
        )
        self.btn_delete_item = QPushButton("Löschen")

        button_row.addWidget(self.new_reward_item_button)
        button_row.addWidget(self.edit_reward_item_button)
        button_row.addWidget(self.duplicate_reward_item_button)
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
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # pyright: ignore[reportAttributeAccessIssue]

        item_list = item_repo.get_all_items()
        self._build_reward_items_table_view_rows(item_list)

    def _build_reward_items_table_view_rows(self, items: list[RewardItem]) -> None:

        if not items:
            row = [QStandardItem("Keine Items vorhanden")]
            # restliche Spalten leer auffüllen
            row += [QStandardItem("") for _ in range(4)]
            for item in row:
                item.setEditable(False)
            self.reward_items_table_view_model.appendRow(row)
            return

        for reward_item in items:
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

    # -----------------------------------------------------------------
    # Slots for this widget
    # -----------------------------------------------------------------

    def on_new_reward_item_button_clicked(self) -> None:
        dialog = RewardItemDialog()
        new_item = dialog.get_data()
        if not new_item:
            return

        item_repo.create_item_by_reward_item(new_item)

        self.reload_reward_items_table_view()

    def _on_reward_items_table_view_selection_changed(self) -> None:
        has_selection = self.reward_items_table_view.selectionModel().hasSelection()
        self.edit_reward_item_button.setEnabled(has_selection)
        self.duplicate_reward_item_button.setEnabled(has_selection)
        self.btn_delete_item.setEnabled(has_selection)

    def on_edit_reward_item_button_clicked(self) -> None:
        selection = self.reward_items_table_view.selectionModel().currentIndex()
        if not selection.isValid():
            return

        row = selection.row()
        item_id_index = self.reward_items_table_view_model.index(row, 0)
        item_id = item_id_index.data()

        dialog = RewardItemDialog(self, item_id=item_id)
        edited_item = dialog.get_data()
        if not edited_item:
            return

        item_repo.update_item_by_reward_item(edited_item)

        self.reload_reward_items_table_view()

    def on_duplicate_reward_item_button_clicked(self) -> None:
        selection = self.reward_items_table_view.selectionModel().currentIndex()
        if not selection.isValid():
            return

        row = selection.row()
        item_id_index = self.reward_items_table_view_model.index(row, 0)
        item_id = item_id_index.data()

        dialog = RewardItemDialog()
        dialog.set_data(item_id, False)
        item_duplicate = dialog.get_data()
        if not item_duplicate:
            return

        item_repo.create_item_by_reward_item(item_duplicate)

        self.reload_reward_items_table_view()
