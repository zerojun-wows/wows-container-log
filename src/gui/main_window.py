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
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTableView,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

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

        # self._create_actions()
        # self._create_toolbar()
        # self._create_container_tab()
        # self._create_drops_tab()
        # self._create_central_widget()

        # ---- new code here -----
        self._create_main_tab_widget()
        self._create_toolbars()

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
        search_panel_widget = QWidget()
        layout = QVBoxLayout()

        title_label = QLabel("Container")
        layout.addWidget(title_label)

        search_line_edit = QLineEdit()
        search_line_edit.setPlaceholderText("Suche...")
        layout.addWidget(search_line_edit)

        self.container_list_view = QListView()
        self.container_list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
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
        self.container_panel_tabwidget.addTab(QWidget(), "Belohnungen und Drop-Regeln")

        return self.container_panel_tabwidget

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

        self.container_pushbutton = QPushButton(
            "Belohnungen generieren / Daten aktualisieren"
        )
        layout.addStretch(1)
        layout.addWidget(self.container_pushbutton)
        layout.addStretch(1)

        return layout

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
        # self.new_container_action.triggered.connect(self.on_new_container)
        self.exit_application_action = QAction("Programm beenden", self)

    # -----------------------------------------------------------------
    # ---- Old Code needs refactor due to bad naming of variables -----
    # -----------------------------------------------------------------#
    def _create_central_widget(self):
        """Create the central widget of the main window."""
        self.central_widget = QTabWidget()
        self.central_widget.addTab(self.drops_tab, "Drops")
        self.central_widget.addTab(self.container_tab, "Containers")
        self.central_widget.setTabPosition(QTabWidget.TabPosition.West)
        self.setCentralWidget(self.central_widget)

    def _create_container_tab(self):
        """Create the container tab of the main window."""
        self.container_tab = QSplitter(Qt.Orientation.Horizontal, self)

        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        self.container_tab.addWidget(left_panel)
        self.container_tab.addWidget(right_panel)

        # self.container_tab.setStretchFactor(0, 1)
        # self.container_tab.setStretchFactor(1, 3)

    def _create_drops_tab(self):
        """Create the drops tab of the main window."""
        self.drops_tab = QWidget()
        drops_layout = QVBoxLayout()
        drops_layout.addWidget(QLabel("Drops - not implemented yet"))
        self.drops_tab.setLayout(drops_layout)

    def _create_left_panel(self):
        """Create the left panel of the container tab."""
        left_panel = QWidget(self)
        left_layout = QVBoxLayout(left_panel)

        label_title = QLabel("Containers")
        left_layout.addWidget(label_title)

        search_line_edit = QLineEdit()
        search_line_edit.setPlaceholderText("Suche...")
        left_layout.addWidget(search_line_edit)

        self.container_list = QListView()
        self.container_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.container_model = QStandardItemModel(self)
        self.container_list.setModel(self.container_model)
        self.reload_container_list()

        left_layout.addWidget(self.container_list)

        left_panel.setLayout(left_layout)
        return left_panel

    def _create_right_panel(self):
        """Create the right panel of the container tab."""
        right_panel = QTabWidget()

        right_panel.addTab(self._create_tab_containerdetails(), "Containerdetails")
        right_panel.addTab(
            self._create_tab_slots_and_groups(), "Belohnungsplätze und Gruppen"
        )
        right_panel.addTab(
            self._create_tab_items_and_entries(), "Belohnungen und Drop-Regeln"
        )
        # ToDo add preview tab later

        return right_panel

    def _create_tab_containerdetails(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()
        self.container_id_edit: QLineEdit = QLineEdit()
        self.container_name_edit = QLineEdit()
        self.container_premium_checkbox = QCheckBox("Premium-Container")
        self.container_slots_spin = QSpinBox()
        self.container_slots_spin.setMinimum(1)
        self.container_slots_spin.setMaximum(5)

        form.addRow("Technische ID:", self.container_id_edit)
        form.addRow("Anzeigename:", self.container_name_edit)
        form.addRow("Premium:", self.container_premium_checkbox)
        form.addRow("Belohnungen:", self.container_slots_spin)

        layout.addLayout(form)

        lbl_desc = QLabel("Beschreibung / Notizen:")
        self.container_description_edit = QPlainTextEdit()
        self.container_description_edit.setPlaceholderText(
            "Z.B. Drop-Logik, Event, Saison ..."
        )

        layout.addWidget(lbl_desc)
        layout.addWidget(self.container_description_edit, 1)

        btn_slots = QPushButton("Belohnungen generieren / Daten aktualisieren")

        hl = QHBoxLayout()
        hl.addStretch(1)
        hl.addWidget(btn_slots)
        hl.addStretch(1)

        layout.addLayout(hl)

        return widget

    def _create_tab_slots_and_groups(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)

        left = QWidget()
        left_layout = QVBoxLayout(left)

        lbl_slots = QLabel("Slots dieses Containers")
        lbl_slots.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(lbl_slots)

        table_slots = QTableView()
        left_layout.addWidget(table_slots, 1)

        btn_row = QHBoxLayout()
        btn_new_group = QPushButton("Neue Gruppe")
        btn_assign_group = QPushButton("Gruppe zuweisen")
        btn_row.addWidget(btn_new_group)
        btn_row.addWidget(btn_assign_group)
        btn_row.addStretch(1)
        left_layout.addLayout(btn_row)

        right = QWidget()
        right_layout = QVBoxLayout(right)

        lbl_group_editor = QLabel("Gruppen-Editor")
        lbl_group_editor.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(lbl_group_editor)

        form = QGridLayout()
        lbl_active_group = QLabel("Aktive Gruppe:")
        cb_group = QComboBox()
        form.addWidget(lbl_active_group, 0, 0)
        form.addWidget(cb_group, 0, 1)

        lbl_gid = QLabel("Gruppen-ID:")
        edit_gid = QLineEdit()
        lbl_gname = QLabel("Name:")
        edit_gname = QLineEdit()

        form.addWidget(lbl_gid, 1, 0)
        form.addWidget(edit_gid, 1, 1)
        form.addWidget(lbl_gname, 2, 0)
        form.addWidget(edit_gname, 2, 1)

        right_layout.addLayout(form)

        tree = QTreeWidget()
        tree.setHeaderLabels(["Gruppenstruktur"])
        # Beispielstruktur
        root_item = QTreeWidgetItem(["group_more_coal_slot1"])
        child_std = QTreeWidgetItem(["group_more_coal_std"])
        child_jp = QTreeWidgetItem(["group_more_coal_jackpot"])
        root_item.addChildren([child_std, child_jp])
        tree.addTopLevelItem(root_item)
        tree.expandAll()

        right_layout.addWidget(tree, 1)

        btn_row2 = QHBoxLayout()
        btn_add_sub = QPushButton("Untergruppe hinzufügen")
        btn_del_sub = QPushButton("Untergruppe entfernen")
        btn_row2.addWidget(btn_add_sub)
        btn_row2.addWidget(btn_del_sub)
        btn_row2.addStretch(1)
        right_layout.addLayout(btn_row2)

        lbl_hint = QLabel(
            "Hinweis:<br> Änderungen an Gruppen wirken auf alle zugeordneten Slots."
        )
        lbl_hint.setWordWrap(True)
        right_layout.addWidget(lbl_hint)

        layout.addWidget(left, 1)
        layout.addWidget(right, 1)

        return widget

    def _create_tab_items_and_entries(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Links: Items
        left = QWidget()
        left_layout = QVBoxLayout(left)

        lbl_items = QLabel("Items (RewardItem)")
        lbl_items.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(lbl_items)

        table_items = QTableView()
        left_layout.addWidget(table_items, 1)

        btn_row = QHBoxLayout()
        btn_new_item = QPushButton("Neues Item")
        btn_dup_item = QPushButton("Item duplizieren")
        btn_del_item = QPushButton("Item löschen")
        btn_row.addWidget(btn_new_item)
        btn_row.addWidget(btn_dup_item)
        btn_row.addWidget(btn_del_item)
        btn_row.addStretch(1)
        left_layout.addLayout(btn_row)

        # Rechts: Einträge
        right = QWidget()
        right_layout = QVBoxLayout(right)

        lbl_entries = QLabel("Einträge (RewardEntry)")
        lbl_entries.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(lbl_entries)

        cb_group = QComboBox()
        cb_group.setPlaceholderText("Gruppe wählen ...")
        right_layout.addWidget(cb_group)

        table_entries = QTableView()
        right_layout.addWidget(table_entries, 1)

        btn_row2 = QHBoxLayout()
        btn_new_entry = QPushButton("Neuer Eintrag")
        btn_del_entry = QPushButton("Eintrag löschen")
        btn_row2.addWidget(btn_new_entry)
        btn_row2.addWidget(btn_del_entry)
        btn_row2.addStretch(1)
        right_layout.addLayout(btn_row2)

        lbl_prob = QLabel(
            "Hinweis: \nSummen der Wahrscheinlichkeiten werden überprüft."
        )
        right_layout.addWidget(lbl_prob)

        layout.addWidget(left, 1)
        layout.addWidget(right, 1)

        return widget

    def reload_container_list(self, select_id: str | None = None) -> None:
        containers = container_repo.list_containers()

        self.container_model.clear()
        # selected_row = -1

        for row, c in enumerate(containers):
            item = QStandardItem(
                f"{c.name} ({c.items} Gegenst{'ände' if c.items != 1 else 'and'}){' - Premiumcontainer' if c.premium == 1 else ''}"
            )
            # ID für spätere Auswahl merken
            item.setData(c.id)
            self.container_model.appendRow(item)

            if select_id is not None and c.id == select_id:
                selected_row = row

        # if selected_row >= 0:
        #     index = self.container_model.index(selected_row, 0)
        #    self.container_list_view.setCurrentIndex(index)

    def on_new_container(self):
        """Reset the container form to create a new container entry.

        This method clears all container-related input fields, resets state, and
        switches the main view to the container tab so the user can enter data
        for a new container.
        """

        self.current_container_id = None

        self.container_id_edit.setText("")
        self.container_name_edit.setText("")
        self.container_premium_checkbox.setChecked(False)
        self.container_slots_spin.setValue(1)
        self.container_description_edit.setPlainText("")

        self.container_id_edit.setReadOnly(False)
        self.container_id_edit.setFocus()

        self.central_widget.setCurrentWidget(self.container_tab)
