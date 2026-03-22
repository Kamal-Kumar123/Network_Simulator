from __future__ import annotations

from typing import Optional, Tuple

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
)


class AddDeviceDialog(QDialog):
    """Dialog used to create a new network device."""

    def __init__(self, parent: Optional[QDialog] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add device")
        layout = QFormLayout(self)

        self.name_input = QLineEdit(self)
        self.type_combo = QComboBox(self)
        self.type_combo.addItems(["EndDevice", "Hub", "Switch", "Bridge"])
        self.mac_input = QLineEdit(self)

        layout.addRow("Name", self.name_input)
        layout.addRow("Type", self.type_combo)
        layout.addRow("MAC (for EndDevice)", self.mac_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_values(self) -> Tuple[str, str, str]:
        """Return the values entered in the dialog."""
        return (
            self.name_input.text().strip(),
            self.type_combo.currentText(),
            self.mac_input.text().strip(),
        )


class ConnectDialog(QDialog):
    """Dialog used to connect two devices."""

    def __init__(self, devices: list[str], parent: Optional[QDialog] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Connect devices")
        layout = QFormLayout(self)

        self.a_combo = QComboBox(self)
        self.a_combo.addItems(devices)
        self.b_combo = QComboBox(self)
        self.b_combo.addItems(devices)

        self.segment_combo = QComboBox(self)
        self.segment_combo.addItems(["A", "B"])

        layout.addRow("Device A", self.a_combo)
        layout.addRow("Device B", self.b_combo)
        layout.addRow("Bridge segment", self.segment_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_values(self) -> Tuple[str, str, str]:
        """Return the selected connection values."""
        return (
            self.a_combo.currentText(),
            self.b_combo.currentText(),
            self.segment_combo.currentText(),
        )

