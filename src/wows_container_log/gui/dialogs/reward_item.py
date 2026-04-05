from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from wows_container_log.models.container import RewardItem
from wows_container_log.storage import item_repo


class RewardItemDialog(QDialog):
    def __init__(self, parent=None, item_id=None):
        super().__init__(parent)

        self.edit_mode: bool = False

        layout = QVBoxLayout(self)
        layout.addLayout(self._create_form_layout())
        layout.addWidget(self._create_dialog_button_box())

        self.setFixedHeight(206)
        self.setMinimumWidth(400)

        if item_id is None:
            self.setWindowTitle("Neues Item anlegen")
        else:
            self.setWindowTitle("Item bearbeiten")
            self.edit_mode = True
            self.item_id_edit.setReadOnly(True)
            self._load_data_into_form(item_id)

    def _create_form_layout(self) -> QFormLayout:
        self._create_form_widgets()
        form_layout = QFormLayout()

        form_layout.addRow("Id:", self.item_id_edit)
        form_layout.addRow("Name:", self.item_name_edit)
        form_layout.addRow("Menge:", self.item_amount_spin)
        form_layout.addRow("Metadaten:", self.item_meta_edit)
        form_layout.addRow("", self.item_unique_once_checkbox)

        return form_layout

    def _create_form_widgets(self) -> None:

        self.item_id_edit = self._create_line_edit_widgets()

        self.item_name_edit = self._create_line_edit_widgets()

        self.item_amount_spin = QSpinBox(self)
        self.item_amount_spin.setMinimum(1)

        self.item_meta_edit = QLineEdit(self)

        self.item_unique_once_checkbox = QCheckBox("Nur einmal droppbar")
        self.item_unique_once_checkbox.setChecked(False)

    def _create_line_edit_widgets(self) -> QLineEdit:
        widget = QLineEdit(self)
        widget.setPlaceholderText("Bitte ausfüllen!")
        widget.editingFinished.connect(self.on_line_or_name_edit_finished)
        return widget

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

    def get_data(self) -> RewardItem | None:
        if self.exec() != QDialog.Accepted:  # pyright: ignore[reportAttributeAccessIssue]
            return None

        self.item_id = self.item_id_edit.text().strip()
        self.name = self.item_name_edit.text().strip()
        self.amount = self.item_amount_spin.value()
        self.meta = self.item_meta_edit.text().strip() or None
        self.unique_once = 1 if self.item_unique_once_checkbox.isChecked() else 0

        if not self._validate_form_values():
            return None

        return RewardItem(
            id=self.item_id,
            name=self.name,
            amount=self.amount,
            meta=self.meta,
            unique_once=self.unique_once,
        )

    def set_data(self, item_id: str, edit_mode: bool = True) -> None:
        if not item_id:
            return

        self.edit_mode = edit_mode
        if self.edit_mode:
            self.item_id_edit.setReadOnly(True)
        else:
            self.item_id_edit.setReadOnly(False)

        self._load_data_into_form(item_id)

    def _validate_form_values(self) -> bool:

        if not self.item_id:
            QMessageBox.warning(self, "Fehler", "ID darf nicht leer sein.")
            return False

        if not self.name:
            QMessageBox.warning(self, "Fehler", "Name darf nicht leer sein.")
            return False

        if not self._is_item_id_unique() and not self.edit_mode:
            QMessageBox.warning(
                self,
                "Fehler",
                f"Ein Item mit der ID '{self.item_id}' existiert bereits.",
            )
            return False

        return True

    def _is_item_id_unique(self) -> bool:
        return item_repo.is_item_unique_by_id(self.item_id)

    def _load_data_into_form(self, item_id: str) -> None:
        loaded_item = item_repo.get_item_by_id(item_id)

        if loaded_item is not None:
            self.item_id_edit.setText(loaded_item.id)
            self.item_name_edit.setText(loaded_item.name)
            self.item_amount_spin.setValue(loaded_item.amount)
            self.item_meta_edit.setText(loaded_item.meta)
            self.item_unique_once_checkbox.setChecked(loaded_item.unique_once == 1)

    # -----------------------------------------------------------------
    # Slots of this dialog
    # -----------------------------------------------------------------
    def on_line_or_name_edit_finished(self) -> None:
        if self.item_id_edit.text().strip() and self.item_name_edit.text().strip():
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)
