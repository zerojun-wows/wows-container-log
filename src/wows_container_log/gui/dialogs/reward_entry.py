from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from wows_container_log.models.container import RewardEntry
from wows_container_log.storage import group_repo, item_repo, entry_repo


class RewardEntryDialog(QDialog):
    def __init__(self, parent_group_id: str, parent=None, entry_id=None) -> None:

        super().__init__(parent)

        self.parent_group_id = parent_group_id

        layout = QVBoxLayout(self)

        layout.addLayout(self._create_form_layout())
        layout.addWidget(self._create_dialog_button_box())

        # self.setFixedHeight(272)
        self.setMinimumWidth(400)

        if entry_id is None:
            self.setWindowTitle("Neue Belohnungsposition anlegen")
        else:
            self.setWindowTitle("Belohnungsposition bearbeiten")

        self._load_parent_data_for_reward_entry_group_label()

    # ----------------------------------------------------------------
    # Creation of dialog widgets
    # ----------------------------------------------------------------

    def _create_form_layout(self) -> QFormLayout:

        self._create_form_widgets()

        form_layout = QFormLayout()

        form_layout.addRow("Id:", self.reward_entry_id_label)
        form_layout.addRow("Gruppe des Eintrags:", self.reward_entry_group_label)
        form_layout.addRow("", QLabel(""))
        form_layout.addRow("Eintragsschlüssel", self.reward_entry_key_line_edit)
        form_layout.addRow("Eintragsart:", self.reward_entry_kind_combo_box)
        form_layout.addRow(
            self.reward_entry_ref_id_label, self.reward_entry_ref_id_combo_box
        )
        form_layout.addRow(
            self.reward_entry_amount_label, self.reward_entry_amount_spin_box
        )
        form_layout.addRow(
            "Wahrscheinlichkeit 0-100 %", self.reward_entry_probability_double_spin_box
        )

        return form_layout

    def _create_form_widgets(self) -> None:

        self.reward_entry_id_label = QLabel(self)
        self.reward_entry_id_label.setToolTip(
            "Dieses Feld wird nur datenbankseitig verwendet"
        )

        self.reward_entry_group_label = QLabel(self)
        self.reward_entry_group_label.setToolTip(
            "Information welcher Gruppe der Eintrag angehört"
        )

        self.reward_entry_key_line_edit = self._create_form_line_edit()

        self._create_form_combo_boxes()

        self._create_form_spin_boxes()

    def _create_form_line_edit(
        self, tool_tip: str | None = None, read_only: bool | None = None
    ) -> QLineEdit:
        line_edit = QLineEdit(self)
        if tool_tip is not None:
            line_edit.setToolTip(tool_tip)
        if read_only is not None:
            line_edit.setReadOnly(read_only)
        return line_edit

    def _create_form_combo_boxes(self) -> None:

        self.reward_entry_kind_combo_box = QComboBox(self)
        self.reward_entry_kind_combo_box.setPlaceholderText("Bitte auswählen")
        self.reward_entry_kind_combo_box.addItem("Untergruppe", "group")
        self.reward_entry_kind_combo_box.addItem("Gegenstand", "item")
        self.reward_entry_kind_combo_box.currentIndexChanged.connect(
            self.on_reward_entry_kind_combo_box_current_index_changed
        )

        self.reward_entry_ref_id_label = QLabel()

        self.reward_entry_ref_id_combo_box = QComboBox(self)
        self.reward_entry_ref_id_combo_box.setVisible(False)
        self.reward_entry_ref_id_combo_box.currentIndexChanged.connect(
            self.on_reward_entry_ref_id_combo_box_current_index_changed
        )

    def _create_form_spin_boxes(self) -> None:

        self.reward_entry_amount_label = QLabel("Anzahl:")
        self.reward_entry_amount_label.setVisible(False)

        self.reward_entry_amount_spin_box = QSpinBox(self)
        self.reward_entry_amount_spin_box.setVisible(False)
        self.reward_entry_amount_spin_box.setMaximum(1000000000)
        self.reward_entry_amount_spin_box.editingFinished.connect(
            self.on_reward_entry_amount_spin_box_editing_finished
        )

        self.reward_entry_probability_double_spin_box = QDoubleSpinBox(self)
        self.reward_entry_probability_double_spin_box.setDecimals(4)
        self.reward_entry_probability_double_spin_box.setMaximum(100)
        self.reward_entry_probability_double_spin_box.setMinimum(0)
        self.reward_entry_probability_double_spin_box.editingFinished.connect(
            self.on_reward_entry_probability_double_spin_box_editing_finished
        )

    def _create_dialog_button_box(self) -> QDialogButtonBox:
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,  # pyright: ignore[reportAttributeAccessIssue]
            Qt.Horizontal,  # pyright: ignore[reportAttributeAccessIssue]
            self,
        )
        self.ok_button = buttons.button(QDialogButtonBox.Ok)  # pyright: ignore[reportAttributeAccessIssue]
        self.ok_button.setEnabled(False)
        self.ok_button.setToolTip(
            "Wird freigeschaltet sobald Id und Name ausgefüllt wurden!"
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        return buttons

    # ----------------------------------------------------------------
    # Data related functions
    # ----------------------------------------------------------------

    def get_data(self) -> RewardEntry | None:
        if self.exec() != QDialog.Accepted:  # pyright: ignore[reportAttributeAccessIssue]
            return None

        if self.reward_entry_id_label.text().strip().isdigit():
            reward_entry_id = int(self.reward_entry_id_label.text().strip())
        else:
            reward_entry_id = None

        reward_entry_group_id = self.parent_group_id
        reward_entry_entry_key = self.reward_entry_key_line_edit.text().strip()
        self.reward_entry_kind = self.reward_entry_kind_combo_box.currentData()
        self.reward_entry_ref_id = self.reward_entry_ref_id_combo_box.currentData()
        reward_entry_amount = self.reward_entry_amount_spin_box.value()
        reward_entry_probability = (
            f"{self.reward_entry_probability_double_spin_box.value()} %"
        )

        if not self._validate_form_values():
            return

        return RewardEntry(
            id=reward_entry_id,
            group_id=reward_entry_group_id,
            entry_key=reward_entry_entry_key,
            kind=self.reward_entry_kind,
            ref_id=self.reward_entry_ref_id,
            amount=reward_entry_amount,
            probability=reward_entry_probability,
        )

    def _load_group_data_for_reward_entry_ref_id_combo_box(self) -> None:

        groups_to_list = group_repo.get_all_groups_without_given_id(
            self.parent_group_id
        )

        if not groups_to_list:
            self.reward_entry_ref_id_combo_box.setPlaceholderText(
                "Keine Gruppen auswählbar"
            )
            return

        # Nur Gruppen anzeigen, die keinen Zyklus erzeugen würden
        # oder noch nicht als Untergruppe der aktuellen Gruppe verwendet wurden
        allowed_groups = []
        for group in groups_to_list:
            if entry_repo.would_create_cycle(
                parent_group_id=self.parent_group_id,
                child_group_id=group.id,
            ):
                continue

            if entry_repo.has_group_child(
                parent_group_id=self.parent_group_id,
                child_group_id=group.id,
            ):
                continue

            allowed_groups.append(group)

        if not allowed_groups:
            self.reward_entry_ref_id_combo_box.setPlaceholderText(
                "Keine Gruppen auswählbar"
            )
            return

        self.reward_entry_ref_id_combo_box.setPlaceholderText("Gruppe auswählen")
        for group in allowed_groups:
            self.reward_entry_ref_id_combo_box.addItem(group.name, group.id)

    def _load_item_data_for_reward_entry_ref_id_combo_box(self) -> None:

        items_to_list = item_repo.get_all_items()

        if items_to_list is not None:
            if len(items_to_list) == 0:
                self.reward_entry_ref_id_combo_box.setPlaceholderText(
                    "Keine Gegenstände auswählbar"
                )

            for item in items_to_list:
                self.reward_entry_ref_id_combo_box.setPlaceholderText(
                    "Gegenstand auswählen"
                )
                self.reward_entry_ref_id_combo_box.addItem(item.name, item.id)

    def _load_parent_data_for_reward_entry_group_label(self) -> None:

        group_data = group_repo.get_group_by_id(self.parent_group_id)

        if group_data is None:
            return

        self.reward_entry_group_label.setText(f"{group_data.name}")

    def _show_amount_line_in_form(self, visible: bool) -> None:

        if not visible:
            self.reward_entry_amount_spin_box.setValue(0)
            self.reward_entry_amount_spin_box.setMinimum(0)
        else:
            self.reward_entry_amount_spin_box.setValue(1)
            self.reward_entry_amount_spin_box.setMinimum(1)

        self.reward_entry_amount_label.setVisible(visible)
        self.reward_entry_amount_spin_box.setVisible(visible)

    def _validate_conditions_to_enable_ok_button(self) -> None:

        if (
            self.reward_entry_kind_combo_box.currentIndex() > -1
            and self.reward_entry_ref_id_combo_box.currentIndex() > -1
        ):
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)

    def _validate_form_values(self) -> bool:

        if not self.reward_entry_kind:
            QMessageBox.warning(self, "Fehler", "Eintragsart darf nicht leer sein.")
            return False

        if not self.reward_entry_ref_id:
            QMessageBox.warning(self, "Fehler", "Referenz_id darf nicht leer sein.")
            return False

        return True

    # -----------------------------------------------------------------
    # Slots of this dialog
    # -----------------------------------------------------------------

    def on_reward_entry_amount_spin_box_editing_finished(self) -> None:
        self._validate_conditions_to_enable_ok_button()

    def on_reward_entry_kind_combo_box_current_index_changed(self, index: int) -> None:

        self.reward_entry_ref_id_combo_box.clear()

        if index == 0:
            self.reward_entry_ref_id_label.setText("Untergruppe:")
            self._show_amount_line_in_form(False)
            self._load_group_data_for_reward_entry_ref_id_combo_box()
        else:
            self.reward_entry_ref_id_label.setText("Gegenstand:")
            self._show_amount_line_in_form(True)
            self._load_item_data_for_reward_entry_ref_id_combo_box()

        if not self.reward_entry_ref_id_label.isVisible():
            self.reward_entry_ref_id_label.setVisible(True)

        if not self.reward_entry_ref_id_combo_box.isVisible():
            self.reward_entry_ref_id_combo_box.setVisible(True)

        self._validate_conditions_to_enable_ok_button()

    def on_reward_entry_probability_double_spin_box_editing_finished(self) -> None:
        self._validate_conditions_to_enable_ok_button()

    def on_reward_entry_ref_id_combo_box_current_index_changed(
        self, index: int
    ) -> None:
        self._validate_conditions_to_enable_ok_button()
