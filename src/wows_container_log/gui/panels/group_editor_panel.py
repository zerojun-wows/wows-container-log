from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)
from typing import List

from wows_container_log.gui.dialogs.reward_group import RewardGroupDialog
from wows_container_log.models.container import RewardGroup
from wows_container_log.storage import group_repo


class GroupEditorPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:

        super().__init__(parent)

        main_layout = QVBoxLayout(self)

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Horizontal)  # pyright: ignore[reportAttributeAccessIssue]

        splitter.addWidget(self._create_reward_groups_left_widget(splitter))

        splitter.addWidget(QLabel("Rechts"))

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        self.edit_reward_group_button.setEnabled(False)
        self.delete_reward_group_button.setEnabled(False)

        self.reload_reward_groups_table_view()

    # ----------------------------------------------------------------
    # Creation code for left side of this widget
    # ----------------------------------------------------------------

    def _create_reward_groups_left_widget(self, splitter: QSplitter) -> QWidget:

        left_widget = QWidget(splitter)
        left_layout = QVBoxLayout(left_widget)

        title_label = QLabel("Belohnungs-Gruppen")
        left_layout.addWidget(title_label)

        left_layout.addWidget(self._create_reward_groups_table_view(left_widget))

        left_layout.addLayout(self._create_reward_groups_button_row_layout())

        return left_widget

    def _create_reward_groups_table_view(self, widget: QWidget) -> QWidget:

        self.reward_groups_table_view = QTableView(widget)
        self.reward_groups_table_view_model = QStandardItemModel(self)

        self.REWARD_GROUPS_TABLE_VIEW_MODEL_HEADER_LABELS = ["Name", "ID"]

        self.reward_groups_table_view_model.setHorizontalHeaderLabels(
            self.REWARD_GROUPS_TABLE_VIEW_MODEL_HEADER_LABELS
        )
        self.reward_groups_table_view.setModel(self.reward_groups_table_view_model)
        self.reward_groups_table_view.setSelectionBehavior(QTableView.SelectRows)  # pyright: ignore[reportAttributeAccessIssue]
        self.reward_groups_table_view.setSelectionMode(QTableView.SingleSelection)  # pyright: ignore[reportAttributeAccessIssue]
        self.reward_groups_table_view.selectionModel().selectionChanged.connect(
            self.on_reward_groups_table_view_selection_changed
        )
        # Bearbeitung in der View deaktivieren (zusätzlich Flags später im Model möglich)
        self.reward_groups_table_view.setEditTriggers(QTableView.NoEditTriggers)  # pyright: ignore[reportAttributeAccessIssue]

        return self.reward_groups_table_view

    def _create_reward_groups_button_row_layout(self) -> QHBoxLayout:

        self._create_reward_groups_buttons()

        button_row = QHBoxLayout()
        button_row.addWidget(self.new_reward_group_button)
        button_row.addWidget(self.edit_reward_group_button)
        button_row.addWidget(self.delete_reward_group_button)
        button_row.addStretch()

        return button_row

    def _create_reward_groups_buttons(self) -> None:

        self.new_reward_group_button = QPushButton("Neu")
        self.new_reward_group_button.clicked.connect(
            self.on_new_reward_group_button_clicked
        )
        self.edit_reward_group_button = QPushButton("Bearbeiten")
        self.edit_reward_group_button.clicked.connect(
            self.on_edit_reward_group_button_clicked
        )
        self.delete_reward_group_button = QPushButton("Löschen")
        self.delete_reward_group_button.clicked.connect(
            self.on_delete_reward_group_button_clicked
        )

    # -----------------------------------------------------------------
    # Creation code for right side of this widget
    # -----------------------------------------------------------------

    # -----------------------------------------------------------------
    # Code for data relevant actions of visual widgets on left side
    # -----------------------------------------------------------------

    def reload_reward_groups_table_view(self) -> None:

        self.reward_groups_table_view_model.clear()
        self.reward_groups_table_view_model.setHorizontalHeaderLabels(
            self.REWARD_GROUPS_TABLE_VIEW_MODEL_HEADER_LABELS
        )
        header = self.reward_groups_table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # pyright: ignore[reportAttributeAccessIssue]

        group_list = group_repo.get_all_groups()

        self._build_reward_groups_table_view_rows(group_list)

    def _build_reward_groups_table_view_rows(
        self, group_list: List[RewardGroup]
    ) -> None:

        if not group_list:
            row = [QStandardItem("Keine Items vorhanden")]
            row += [QStandardItem("")]

            for item in row:
                item.setEditable(False)
                # Platzhalterzeile nicht auswählbar machen
                item.setFlags(Qt.ItemIsEnabled)  # pyright: ignore[reportAttributeAccessIssue]

            self.reward_groups_table_view_model.appendRow(row)

            return

        for reward_group in group_list:
            row = [QStandardItem(reward_group.name), QStandardItem(reward_group.id)]

            for item in row:
                item.setEditable(False)

            self.reward_groups_table_view_model.appendRow(row)

    # -----------------------------------------------------------------
    # Code for data relevant actions of visual widgets on right side
    # -----------------------------------------------------------------

    # -----------------------------------------------------------------
    # Slots for this widget's left side (alphabetically ordered)
    # -----------------------------------------------------------------

    def on_delete_reward_group_button_clicked(self) -> None:
        selection = self.reward_groups_table_view.selectionModel().currentIndex()
        if not selection.isValid():
            return

        row = selection.row()
        group_id_index = self.reward_groups_table_view_model.index(row, 1)
        group_id = group_id_index.data()

        reply = QMessageBox.question(
            self,
            "Gruppe löschen",
            f"Soll die Gruppe '{group_id}' wirklich entfernt werden?",
            QMessageBox.Yes | QMessageBox.No,  # pyright: ignore[reportAttributeAccessIssue]
            QMessageBox.No,  # pyright: ignore[reportAttributeAccessIssue]
        )
        if reply != QMessageBox.Yes:  # pyright: ignore[reportAttributeAccessIssue]
            return

        group_repo.delete_group_by_id(group_id)

        self.reload_reward_groups_table_view()

    def on_edit_reward_group_button_clicked(self) -> None:
        selection = self.reward_groups_table_view.selectionModel().currentIndex()
        if not selection.isValid():
            return

        row = selection.row()
        group_id_index = self.reward_groups_table_view_model.index(row, 1)
        group_id = group_id_index.data()

        dialog = RewardGroupDialog(self, group_id=group_id)
        edited_group = dialog.get_data()
        if not edited_group:
            return

        group_repo.update_group_by_reward_group(edited_group)

        self.reload_reward_groups_table_view()

    def on_new_reward_group_button_clicked(self) -> None:

        dialog = RewardGroupDialog()
        new_group = dialog.get_data()

        if not new_group:
            return

        group_repo.create_group_by_reward_group(new_group)

        self.reload_reward_groups_table_view()

    def on_reward_groups_table_view_selection_changed(
        self, selected, deselected
    ) -> None:
        has_selection = self.reward_groups_table_view.selectionModel().hasSelection()
        self.edit_reward_group_button.setEnabled(has_selection)
        # self.duplicate_reward_item_button.setEnabled(has_selection)
        self.delete_reward_group_button.setEnabled(has_selection)

    # -----------------------------------------------------------------
    # Slots for this widget's right side
    # -----------------------------------------------------------------
