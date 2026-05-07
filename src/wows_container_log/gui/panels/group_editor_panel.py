from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableView,
    QTreeView,
    QVBoxLayout,
    QWidget,
)
from typing import List

from wows_container_log.gui.dialogs.reward_entry import RewardEntryDialog
from wows_container_log.gui.dialogs.reward_group import RewardGroupDialog
from wows_container_log.models.container import RewardEntry, RewardGroup
from wows_container_log.storage import entry_repo, group_repo, item_repo
from wows_container_log.storage.entry_repo import (
    CyclicGroupError,
    DuplicateGroupChildError,
    DuplicateItemChildError,
)


class GroupEditorPanel(QWidget):
    REWARD_GROUPS_TABLE_VIEW_MODEL_HEADER_LABELS = ["Name", "ID"]
    REWARD_ENTRIES_TREE_VIEW_MODEL_HEADER_LABELS = [
        "Name",
        "Anzahl",
        "Wahrscheinlichkeit",
        "Eintragsschlüssel",
        "jeweilige ID",
    ]

    def __init__(self, parent: QWidget | None = None) -> None:

        super().__init__(parent)

        main_layout = QVBoxLayout(self)

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Horizontal)  # pyright: ignore[reportAttributeAccessIssue]

        splitter.addWidget(self._create_reward_groups_left_widget(splitter))

        splitter.addWidget(self._create_reward_entries_of_group_right_widget(splitter))

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        self.edit_reward_group_button.setEnabled(False)
        self.delete_reward_group_button.setEnabled(False)

        self.reload_reward_groups_table_view()
        self.reload_reward_entries_tree_view()

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

    def _create_reward_entries_of_group_right_widget(
        self, splitter: QSplitter
    ) -> QWidget:

        right_widget = QWidget(splitter)
        right_layout = QVBoxLayout(right_widget)

        title_label = QLabel("Drop-Einträge")
        right_layout.addWidget(title_label)

        right_layout.addWidget(self._create_reward_entries_tree_view_widget())
        right_layout.addLayout(self._create_reward_entries_button_row_layout())

        return right_widget

    def _create_reward_entries_tree_view_widget(self) -> QWidget:

        self.reward_entries_tree_view = QTreeView()
        self.reward_entries_tree_view_model = QStandardItemModel(self)
        self.reward_entries_tree_view_model.setHorizontalHeaderLabels(
            self.REWARD_ENTRIES_TREE_VIEW_MODEL_HEADER_LABELS
        )

        self.reward_entries_tree_view.setModel(self.reward_entries_tree_view_model)
        self.reward_entries_tree_view.setSelectionBehavior(QTreeView.SelectRows)  # pyright: ignore[reportAttributeAccessIssue]
        self.reward_entries_tree_view.setSelectionMode(QTreeView.SingleSelection)  # pyright: ignore[reportAttributeAccessIssue]
        self.reward_entries_tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)  # pyright: ignore[reportAttributeAccessIssue]

        return self.reward_entries_tree_view

    def _create_reward_entries_button_row_layout(self) -> QHBoxLayout:
        button_row = QHBoxLayout()

        self.new_reward_entry_button = QPushButton("Neu")
        self.new_reward_entry_button.clicked.connect(
            self.on_new_reward_entry_button_clicked
        )
        button_row.addWidget(self.new_reward_entry_button)
        button_row.addStretch()

        return button_row

    # -----------------------------------------------------------------
    # Code for data relevant actions of visual widgets on left side
    # -----------------------------------------------------------------

    def get_selected_group_id_in_rewards_table_view(self) -> str | None:
        selection = self.reward_groups_table_view.selectionModel().currentIndex()
        if not selection.isValid():
            return

        row = selection.row()
        group_id_index = self.reward_groups_table_view_model.index(row, 1)
        return group_id_index.data()

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
            row = [QStandardItem("Keine Gruppen vorhanden")]
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

    def reload_reward_entries_tree_view(self) -> None:
        self.reward_entries_tree_view_model.clear()
        self.reward_entries_tree_view_model.setHorizontalHeaderLabels(
            self.REWARD_ENTRIES_TREE_VIEW_MODEL_HEADER_LABELS
        )
        header = self.reward_entries_tree_view.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # pyright: ignore[reportAttributeAccessIssue]

        group_id = self.get_selected_group_id_in_rewards_table_view()
        if group_id is None:
            root = QStandardItem("Es ist keine Gruppe ausgewählt")
            self.reward_entries_tree_view_model.appendRow(root)
            return
        else:
            self._build_reward_entries_tree_view_rows(group_id)

        self.reward_entries_tree_view.expandAll()

    def _build_reward_entries_tree_view_rows(self, group_id: str) -> None:

        group = group_repo.get_group_by_id(group_id)
        if not group:
            return

        root_row = self._build_single_row_for_reward_entries_tree_view(
            name=group.name, ref_id=group.id
        )
        self.reward_entries_tree_view_model.appendRow(root_row)

        root_item = root_row[0]

        # Rekursiv alle Einträge (Items + Untergruppen) anhängen
        self._append_entries_to_parent_item_entry_recursive(
            parent_item=root_item,
            group_id=group.id,
            visited=set(),
        )

    def _build_single_row_for_reward_entries_tree_view(
        self,
        name: str,
        amount: str | None = None,
        probability: str | None = None,
        entry_key: str | None = None,
        ref_id: str | None = None,
    ) -> List[QStandardItem]:
        row = [
            QStandardItem(name),
            QStandardItem(amount or ""),
            QStandardItem(probability or ""),
            QStandardItem(entry_key or ""),
            QStandardItem(ref_id or ""),
        ]
        for item in row:
            item.setEditable(False)
            item.setFlags(Qt.ItemIsEnabled)  # pyright: ignore[reportAttributeAccessIssue]

        return row

    def _append_entries_to_parent_item_entry_recursive(
        self,
        parent_item: QStandardItem,
        group_id: str,
        visited: set[str],
    ) -> None:
        # Falls doch irgendwo ein Zyklus in den Daten wäre, brechen wir sicher ab.
        if group_id in visited:
            return

        visited.add(group_id)

        entries = entry_repo.get_all_entries_by_group_id(group_id)

        if not entries:
            self._append_no_entries_placeholder_to_parent_entry(parent_item)
            return

        for entry in entries:
            entry_row = self._append_entry_row_to_parent_item(entry, parent_item)
            self._append_subgroup_entries_if_needed(entry, entry_row, visited)

    def _append_entry_row_to_parent_item(
        self, entry: RewardEntry, parent_item: QStandardItem
    ) -> QStandardItem:
        name = self._get_ref_name_for_entry(entry.kind, entry.ref_id)

        entry_row = self._build_single_row_for_reward_entries_tree_view(
            name=name,
            amount=str(entry.amount),
            probability=entry.probability,
            entry_key=entry.entry_key,
            ref_id=entry.ref_id,
        )
        # RewardEntry.id am ersten Item speichern (für spätere Edit-/Delete-Aktionen)
        entry_row[0].setData(entry.id, Qt.UserRole)  # pyright: ignore[reportAttributeAccessIssue]

        parent_item.appendRow(entry_row)

        return entry_row

    def _append_subgroup_entries_if_needed(
        self,
        entry: RewardEntry,
        entry_row: List[QStandardItem],
        visited: set[str],
    ) -> None:
        # Wenn der Eintrag eine Untergruppe ist, rekursiv deren Inhalte anhängen
        if entry.kind != "group":
            return

        subgroup_id = entry.ref_id
        subgroup_item = entry_row[0]

        self._append_entries_to_parent_item_entry_recursive(
            parent_item=subgroup_item,
            group_id=subgroup_id,
            visited=visited,
        )

    def _append_no_entries_placeholder_to_parent_entry(
        self, parent_item: QStandardItem
    ) -> None:
        no_entry_items = self._build_single_row_for_reward_entries_tree_view(
            name="Keine Einträge vorhanden"
        )
        parent_item.appendRow(no_entry_items)

    def _append_entries_to_parent_entry(
        self, parent_item: QStandardItem, entries: List[RewardEntry]
    ) -> None:
        for entry in entries:
            entry_row = self._build_single_row_for_reward_entries_tree_view(
                name=self._get_ref_name_for_entry(entry.kind, entry.ref_id),
                amount=str(entry.amount),
                probability=entry.probability,
                entry_key=entry.entry_key,
                ref_id=entry.ref_id,
            )
            entry_row[0].setData(entry.id, Qt.UserRole)  # pyright: ignore[reportAttributeAccessIssue]

            parent_item.appendRow(entry_row)

    def _get_ref_name_for_entry(self, kind: str, ref_id: str) -> str:
        ref_name = (
            entry_repo.resolve_entry_name_by_kind_and_ref_id(kind, ref_id)
            or ref_id  # Fallback
        )
        if kind == "item":
            if data := self._get_meta_information_from_item(ref_id):
                ref_name += f"     -     {data} "

        return ref_name

    def _get_meta_information_from_item(self, item_id) -> str | None:
        item_data = item_repo.get_item_by_id(item_id)
        if item_data is not None and item_data.meta is not None:
            return item_data.meta

    # -----------------------------------------------------------------
    # Slots for this widget's left side (alphabetically ordered)
    # -----------------------------------------------------------------

    def on_delete_reward_group_button_clicked(self) -> None:

        group_id = self.get_selected_group_id_in_rewards_table_view()
        if not group_id:
            return

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

        group_id = self.get_selected_group_id_in_rewards_table_view()
        if not group_id:
            return

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

        # for right widget
        self.reload_reward_entries_tree_view()

    # -----------------------------------------------------------------
    # Slots for this widget's right side
    # -----------------------------------------------------------------

    def on_new_reward_entry_button_clicked(self) -> None:
        # sourcery skip: reintroduce-else, swap-if-else-branches, use-named-expression
        parent_group_id = self.get_selected_group_id_in_rewards_table_view()
        if parent_group_id is None:
            return

        dialog = RewardEntryDialog(parent_group_id=parent_group_id)
        new_entry = dialog.get_data()

        if not new_entry:
            return

        try:
            entry_repo.create_entry_by_reward_entry(new_entry)
        except CyclicGroupError as exc:
            QMessageBox.warning(
                self,
                "Ungültige Gruppen-Zuordnung",
                str(exc),
            )
            return
        except DuplicateGroupChildError as exc:
            QMessageBox.warning(self, "Doppelte Untergruppe", str(exc))
            return
        except DuplicateItemChildError as exc:
            QMessageBox.warning(self, "Doppelter Gegenstand", str(exc))
            return

        self.reload_reward_entries_tree_view()
