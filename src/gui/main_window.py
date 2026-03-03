"""
This module contains the main window of the application.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTableView,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)
from src.models.container import ContainerType
from src.storage import container_repo
from versioning import get_version


class MainWindow(QMainWindow):
    """
    This class is the main window of the application.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            f"World Of Warships Container Log {get_version('wows-container-log')}"
        )
        self.setGeometry(100, 100, 1024, 600)

        self._create_main_tab_widget()
        self._create_toolbars()

        self.reload_container_list_view()

    def _create_main_tab_widget(self) -> None:
        self.main_tab_widget = QTabWidget()
        self.main_tab_widget.addTab(self._create_main_drops_widget(), "Drops")
        self.main_tab_widget.addTab(self._create_main_container_widget(), "Container")
        self.main_tab_widget.setTabPosition(QTabWidget.TabPosition.West)

        self.setCentralWidget(self.main_tab_widget)

    # -----------------------------------------------------------------
    # Creation code for drop logging part of application
    # -----------------------------------------------------------------
    def _create_main_drops_widget(self) -> QWidget:
        """Create the main tab widget used as the central content area.

        This method initializes the main tab widget, adds the primary drops tab,
        and assigns it as the central widget of the main window.
        """
        self.main_drops_widget = QWidget()

        layout = QVBoxLayout()

        placeholder_label = QLabel("Drops - not implemented yet")
        placeholder_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(placeholder_label)
        self.main_drops_widget.setLayout(layout)

        return self.main_drops_widget

    # -----------------------------------------------------------------
    # Creation code for container definition part of application
    # -----------------------------------------------------------------
    def _create_main_container_widget(self) -> QSplitter:
        self.main_container_widget = QSplitter(Qt.Orientation.Horizontal, self)

        self.main_container_widget.addWidget(self._create_search_panel_widget())
        self.main_container_widget.addWidget(self._create_container_panel_tabwidget())

        return self.main_container_widget

    def _create_search_panel_widget(self) -> QWidget:
        # sourcery skip: class-extract-method
        search_panel_widget = QWidget()
        layout = QVBoxLayout()

        title_label = QLabel("Container")
        layout.addWidget(title_label)

        search_line_edit = QLineEdit()
        search_line_edit.setPlaceholderText("Suche...")
        layout.addWidget(search_line_edit)

        self.container_list_view = QListView()
        self.container_list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.container_list_view.clicked.connect(self.on_container_list_view_clicked)
        self.container_list_view_model = QStandardItemModel(self)
        self.container_list_view_model.appendRow(QStandardItem("Testzeile"))
        self.container_list_view.setModel(self.container_list_view_model)
        layout.addWidget(self.container_list_view)

        search_panel_widget.setLayout(layout)

        return search_panel_widget

    def _create_container_panel_tabwidget(self) -> QTabWidget:
        self.container_panel_tabwidget = QTabWidget()

        self.container_panel_tabwidget.addTab(
            self._create_subtab_containerdetails_widget(), "Containerdetails"
        )
        self.container_panel_tabwidget.addTab(
            self._create_subtab_slots_and_groups_widget(),
            "Belohnungsplätze und Gruppen",
        )
        self.container_panel_tabwidget.addTab(
            self._create_subtab_items_and_entries_widget(),
            "Belohnungen und Drop-Regeln",
        )

        return self.container_panel_tabwidget

    # First sub tab creation
    def _create_subtab_containerdetails_widget(self) -> QWidget:
        self.subtab_containerdetails_widget = QWidget()

        layout = QVBoxLayout()
        layout.addLayout(self._create_subtab_containerdetails_formlayout())

        container_description_label = QLabel("Beschreibung / Notizen:")
        self.container_description_plainedit = QPlainTextEdit()
        self.container_description_plainedit.setPlaceholderText(
            "Z.B. Drop-Logik, Event, Saison ..."
        )
        layout.addWidget(container_description_label)
        layout.addWidget(self.container_description_plainedit)

        layout.addLayout(self._create_subtab_containerdetails_buttonlayout())

        self.subtab_containerdetails_widget.setLayout(layout)

        return self.subtab_containerdetails_widget

    def _create_subtab_containerdetails_formlayout(self) -> QFormLayout:
        layout = QFormLayout()

        self.container_id_edit: QLineEdit = QLineEdit()
        self.container_name_edit = QLineEdit()
        self.container_premium_checkbox = QCheckBox("Premium-Container")
        self.container_slots_spin = QSpinBox()
        self.container_slots_spin.setMinimum(1)
        self.container_slots_spin.setMaximum(5)

        layout.addRow("Technische ID:", self.container_id_edit)
        layout.addRow("Anzeigename:", self.container_name_edit)
        layout.addRow("Premium:", self.container_premium_checkbox)
        layout.addRow("Belohnungen:", self.container_slots_spin)

        return layout

    def _create_subtab_containerdetails_buttonlayout(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self.container_save_pushbutton = QPushButton(
            "Belohnungen generieren / Daten aktualisieren"
        )
        self.container_save_pushbutton.clicked.connect(
            self.on_container_save_pushbutton_clicked
        )
        layout.addStretch(1)
        layout.addWidget(self.container_save_pushbutton)
        layout.addStretch(1)

        return layout

    # Second sub tab creation
    def _create_subtab_slots_and_groups_widget(self) -> QWidget:
        self.subtab_slots_and_groups_widget = QWidget()

        layout = QHBoxLayout()
        layout.addLayout(self._create_slot_display_layout(), 1)
        layout.addLayout(self._create_group_editor_layout(), 1)

        self.subtab_slots_and_groups_widget.setLayout(layout)

        return self.subtab_slots_and_groups_widget

    def _create_slot_display_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        slots_label = QLabel("Belohnungen")
        layout.addWidget(slots_label)

        self.slots_table_view = QTableView()
        layout.addWidget(self.slots_table_view)

        sublayout_buttons = QHBoxLayout()

        new_group_button = QPushButton("Neue Gruppe")
        sublayout_buttons.addWidget(new_group_button)

        assign_group_button = QPushButton("Gruppe zuweisen")
        sublayout_buttons.addWidget(assign_group_button)

        layout.addLayout(sublayout_buttons)
        return layout

    def _create_group_editor_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        group_editor_label = QLabel("Gruppeneditor")
        layout.addWidget(group_editor_label)

        layout.addLayout(self._create_group_editor_form_sublayout())

        self.group_structure_tree = QTreeWidget()
        self.group_structure_tree.setHeaderLabels(["Gruppenstruktur"])

        layout.addWidget(self.group_structure_tree)

        layout.addLayout(self._create_group_editor_button_sublayout())

        hint_label = QLabel(
            "Hinweis:\nÄnderungen an Gruppen wirken auf alle zugeordneten Slots."
        )
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)

        return layout

    def _create_group_editor_form_sublayout(self) -> QFormLayout:
        sublayout = QFormLayout()

        self.active_group_combo = QComboBox()
        self.group_id_edit = QLineEdit()
        self.group_name_edit = QLineEdit()

        sublayout.addRow("Aktive Gruppe:", self.active_group_combo)
        sublayout.addRow("Gruppen-ID:", self.group_id_edit)
        sublayout.addRow("Name:", self.group_name_edit)

        return sublayout

    def _create_group_editor_button_sublayout(self) -> QHBoxLayout:
        sublayout = QHBoxLayout()

        self.add_child_group_button = QPushButton("Untergruppe hinzufügen")
        sublayout.addWidget(self.add_child_group_button)

        self.remove_child_group_button = QPushButton("Untergruppe entfernen")
        sublayout.addWidget(self.remove_child_group_button)

        return sublayout

    # third sub tab creation
    def _create_subtab_items_and_entries_widget(self) -> QWidget:
        self.subtab_items_and_entries_widget = QWidget()

        layout = QHBoxLayout()
        layout.addLayout(self._create_reward_item_editor_layout())
        layout.addLayout(self._create_reward_entry_editor_layout())

        self.subtab_items_and_entries_widget.setLayout(layout)

        return self.subtab_items_and_entries_widget

    def _create_reward_item_editor_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        reward_item_label = QLabel("Items (RewardItem)")
        layout.addWidget(reward_item_label)

        reward_items_table_view = QTableView()
        layout.addWidget(reward_items_table_view)

        sublayout = QHBoxLayout()

        new_reward_item_button = QPushButton("Neues Item")
        sublayout.addWidget(new_reward_item_button)

        duplicate_reward_item_button = QPushButton("Item duplizieren")
        sublayout.addWidget(duplicate_reward_item_button)

        delete_reward_item_button = QPushButton("Item löschen")
        sublayout.addWidget(delete_reward_item_button)

        sublayout.addStretch(1)

        layout.addLayout(sublayout)

        return layout

    def _create_reward_entry_editor_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        reward_entry_label = QLabel("Einträge (RewardEntry)")
        layout.addWidget(reward_entry_label)

        reward_entry_group_combo = QComboBox()
        reward_entry_group_combo.setPlaceholderText("Gruppe wählen ...")
        layout.addWidget(reward_entry_group_combo)

        reward_entry_table = QTableView()
        layout.addWidget(reward_entry_table, 1)

        sublayout = QHBoxLayout()

        new_reward_entry_button = QPushButton("Neuer Eintrag")
        sublayout.addWidget(new_reward_entry_button)

        delete_reward_entry_button = QPushButton("Eintrag löschen")
        sublayout.addWidget(delete_reward_entry_button)

        layout.addLayout(sublayout)

        hint_label = QLabel(
            "Hinweis:\nSummen der Wahrscheinlichkeiten werden überprüft."
        )
        layout.addWidget(hint_label)

        return layout

    # -----------------------------------------------------------------
    # Code for Toolbars
    # -----------------------------------------------------------------
    def _create_toolbars(self) -> None:
        self._create_toolbar_actions()

        self.toolbar = self.addToolBar("Container")
        self.toolbar.addAction(self.new_container_action)

        self.toolbar = self.addToolBar("Application")
        self.toolbar.addAction(self.exit_application_action)

    def _create_toolbar_actions(self) -> None:
        self.new_container_action = QAction("Neuer Container", self)
        self.new_container_action.triggered.connect(
            self.on_new_container_tool_button_triggered
        )

        self.exit_application_action = QAction("Programm beenden", self)
        self.exit_application_action.triggered.connect(self.close)

    # -----------------------------------------------------------------
    # Slots of this application
    # -----------------------------------------------------------------
    def on_new_container_tool_button_triggered(self) -> None:
        self.current_container_id = None

        self.container_id_edit.setText("")
        self.container_name_edit.setText("")
        self.container_premium_checkbox.setChecked(False)
        self.container_slots_spin.setValue(1)
        self.container_description_plainedit.setPlainText("")

        self.container_id_edit.setReadOnly(False)
        self.container_id_edit.setFocus()

        self.main_tab_widget.setCurrentWidget(self.main_container_widget)
        self.container_panel_tabwidget.setCurrentWidget(
            self.subtab_containerdetails_widget
        )

    def on_container_save_pushbutton_clicked(self) -> None:
        # form validation
        if not self._validate_container_form():
            return

        container_id = self.container_id_edit.text().strip()
        container_name = self.container_name_edit.text().strip()
        container_premium = self.container_premium_checkbox.isChecked()
        container_items = self.container_slots_spin.value()
        container_description = self.container_description_plainedit.toPlainText()

        if self.current_container_id is None:
            # neuer container
            container = ContainerType(
                id=container_id,
                name=container_name,
                premium=container_premium,
                items=container_items,
                description=container_description,
            )
        else:
            container = container_repo.get_container_by_id(self.current_container_id)

            if container is None:
                container = container = ContainerType(
                    id=container_id,
                    name=container_name,
                    premium=container_premium,
                    items=container_items,
                    description=container_description,
                )
            else:
                container.name = container_name
                container.premium = container_premium
                container.items = container_items
                container.description = container_description

        saved = container_repo.save_container(container)

        self.current_container_id = saved.id
        self.container_id_edit.setReadOnly(True)

        self.reload_container_list_view(select_id=saved.id)

    def on_container_list_view_clicked(self, index) -> None:
        container_id = index.data(Qt.UserRole)
        self.load_container_into_form(container_id)

    # -----------------------------------------------------------------
    # Form validation routines
    # -----------------------------------------------------------------
    def _validate_container_form(self) -> bool:
        if self.container_id_edit.text() == "":
            QMessageBox.critical(
                self,
                "Keine Container Id",
                "Jeder Container muss eine eindeutige Id besitzen!",
            )
            self.container_id_edit.setFocus()
            return False

        if self.container_name_edit.text() == "":
            QMessageBox.critical(
                self,
                "Kein Container Name",
                "Jeder Container muss einen Namen bekommen!",
            )
            self.container_name_edit.setFocus()
            return False

        # eindeutige container id
        container = container_repo.get_container_by_id(
            self.container_id_edit.text().strip()
        )
        if container is not None and self.current_container_id is None:
            QMessageBox.critical(
                self,
                "Container Id bereits vorhanden",
                "Jeder Container muss eine eindeutige Id besitzen!",
            )
            self.container_id_edit.setFocus()
            return False

        return True

    # -----------------------------------------------------------------
    # Routines to fill widgets with data
    # -----------------------------------------------------------------
    def reload_container_list_view(self, select_id: str | None = None) -> None:
        containers = container_repo.list_containers()

        self.container_list_view_model.clear()
        selected_row = -1

        for row, entry in enumerate(containers):
            item = QStandardItem(
                self._format_container_list_entry(
                    entry.name, entry.items, entry.premium
                )
            )
            item.setData(entry.id, Qt.UserRole)
            print(f"EntryId:{entry.id}")
            self.container_list_view_model.appendRow(item)

            if select_id is not None and entry.id == select_id:
                selected_row = row

        if selected_row >= 0:
            index = self.container_list_view_model.index(selected_row, 0)
            self.container_list_view.setCurrentIndex(index)

    def _format_container_list_entry(self, name: str, items: int, premium: int) -> str:
        item_label = "Gegenstände" if items != 1 else "Gegenstand"
        premium_suffix = " - Premiumcontainer" if premium == 1 else ""
        return f"{name} ({items} {item_label}){premium_suffix}"

    def load_container_into_form(self, container_id: str) -> None:
        container = container_repo.get_container_by_id(container_id)
        if container is None:
            return

        self.current_container_id = container.id

        self.container_id_edit.setText(container.id)
        self.container_id_edit.setReadOnly(True)
        self.container_name_edit.setText(container.name)
        self.container_premium_checkbox.setChecked(bool(container.premium))
        self.container_slots_spin.setValue(container.items)
        self.container_description_plainedit.setPlainText(container.description)

    # -----------------------------------------------------------------
    # Old code and other stuff that will be removed later
    # -----------------------------------------------------------------
