from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from wows_container_log.models.container import RewardGroup
from wows_container_log.storage import group_repo


class RewardGroupDialog(QDialog):
    def __init__(self, parent=None, group_id=None) -> None:

        super().__init__(parent)

        self.edit_mode: bool = False

        layout = QVBoxLayout(self)
        layout.addLayout(self._create_form_layout())
        layout.addWidget(self._create_dialog_button_box())

        self.setFixedHeight(112)
        self.setMinimumWidth(400)

        if group_id is None:
            self.setWindowTitle("Neue Gruppe anlegen")
        else:
            self.setWindowTitle("Gruppe bearbeiten")
            self.set_edit_mode(True)
            self._load_data_into_form(group_id)

    def _load_data_into_form(self, group_id: str) -> None:
        loaded_group = group_repo.get_group_by_id(group_id)

        if loaded_group is not None:
            self.group_id_line_edit.setText(loaded_group.id)
            self.group_name_line_edit.setText(loaded_group.name)

    # ----------------------------------------------------------------
    # Creation of dialog widgets
    # ----------------------------------------------------------------

    def _create_form_layout(self) -> QFormLayout:

        self.group_id_line_edit = self._create_line_edit_widgets()

        self.group_name_line_edit = self._create_line_edit_widgets()

        form_layout = QFormLayout()

        form_layout.addRow("Id:", self.group_id_line_edit)
        form_layout.addRow("Name:", self.group_name_line_edit)

        return form_layout

    def _create_line_edit_widgets(self) -> QLineEdit:
        widget = QLineEdit(self)
        widget.setPlaceholderText("Bitte ausfüllen!")
        widget.editingFinished.connect(
            self.on_group_id_line_edit_or_group_name_line_edit_finished
        )
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

    # ----------------------------------------------------------------
    # Data related functions
    # ----------------------------------------------------------------

    def get_data(self) -> RewardGroup | None:

        if self.exec() != QDialog.Accepted:  # pyright: ignore[reportAttributeAccessIssue]
            return None

        self.group_id = self.group_id_line_edit.text().strip()
        self.group_name = self.group_name_line_edit.text().strip()

        if not self._validate_form_values():
            return None

        return RewardGroup(id=self.group_id, name=self.group_name)

    def _validate_form_values(self) -> bool:

        if not self.group_id:
            QMessageBox.warning(self, "Fehler", "ID darf nicht leer sein.")
            return False

        if not self.group_name:
            QMessageBox.warning(self, "Fehler", "Name darf nicht leer sein.")
            return False

        if not self._is_group_id_unique() and not self.edit_mode:
            QMessageBox.warning(
                self,
                "Fehler",
                f"Ein Item mit der ID '{self.group_id}' existiert bereits.",
            )
            return False

        return True

    def _is_group_id_unique(self) -> bool:
        return group_repo.is_group_unique_by_id(self.group_id)

    def set_edit_mode(self, value: bool) -> None:
        if value:
            self.edit_mode = value
            self.group_id_line_edit.setReadOnly(value)
        else:
            self.edit_mode = False
            self.group_id_line_edit.setReadOnly(False)

    # -----------------------------------------------------------------
    # Slots of this dialog
    # -----------------------------------------------------------------

    def on_group_id_line_edit_or_group_name_line_edit_finished(self) -> None:
        if (
            self.group_id_line_edit.text().strip()
            and self.group_name_line_edit.text().strip()
        ):
            self.ok_button.setEnabled(True)
            self.ok_button.setFocus()
        else:
            self.ok_button.setEnabled(False)
