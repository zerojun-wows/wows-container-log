"""
This module contains the main window of the application.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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

        self._create_container_tab()
        self._create_drops_tab()
        self._create_central_widget()

    def _create_central_widget(self):
        """
        Create the central widget of the main window.
        """
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
        # ToDo: Add model to the list view
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
        right_panel.addTab(self._create_tab_items_and_entries(), "Belohnungen und Drop-Regeln")

        # right_layout = QVBoxLayout(right_panel)
        # right_layout.addWidget(QLabel("Right panel - not implemented yet"))
        # right_panel.setLayout(right_layout)
        return right_panel

    def _create_tab_containerdetails(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()
        self.container_id_edit = QLineEdit()
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
        edit_desc = QPlainTextEdit()
        edit_desc.setPlaceholderText("Z.B. Drop-Logik, Event, Saison ...")

        layout.addWidget(lbl_desc)
        layout.addWidget(edit_desc, 1)

        btn_slots = QPushButton("Belohnungen generieren / Daten aktualisieren")
        # btn_slots.setFixedWidth(220)
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
            "Hinweis: Änderungen an Gruppen wirken auf alle zugeordneten Slots."
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

        lbl_prob = QLabel("Hinweis: \nSummen der Wahrscheinlichkeiten werden überprüft.")
        right_layout.addWidget(lbl_prob)

        layout.addWidget(left, 1)
        layout.addWidget(right, 1)

        return widget
