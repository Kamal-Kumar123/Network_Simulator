from __future__ import annotations

from typing import List, Optional

from PyQt5.QtCore import pyqtSignal

from simulator.engine import BROADCAST_RECEIVER
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QTextEdit,
    QSpinBox,
    QGroupBox,
)


class ControlPanel(QWidget):
    """Panel providing basic frame transmission controls."""

    send_requested = pyqtSignal(str, str, str, bool, bool, bool)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Sender"))
        self.sender_combo = QComboBox()
        row1.addWidget(self.sender_combo)
        row1.addWidget(QLabel("Receiver"))
        self.receiver_combo = QComboBox()
        row1.addWidget(self.receiver_combo)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Data"))
        self.data_input = QLineEdit()
        row2.addWidget(self.data_input)
        layout.addLayout(row2)

        row3 = QHBoxLayout()
        self.chk_crc = QCheckBox("Use CRC")
        self.chk_csma = QCheckBox("Use CSMA/CD")
        self.chk_error = QCheckBox("Inject bit error")
        row3.addWidget(self.chk_crc)
        row3.addWidget(self.chk_csma)
        row3.addWidget(self.chk_error)
        self.btn_send = QPushButton("Send frame")
        row3.addWidget(self.btn_send)
        layout.addLayout(row3)

        self.btn_send.clicked.connect(self._emit_send)

    def _emit_send(self) -> None:
        """Emit the send_requested signal with current form values."""
        self.send_requested.emit(
            self.sender_combo.currentText(),
            self.receiver_combo.currentText(),
            self.data_input.text(),
            self.chk_crc.isChecked(),
            self.chk_csma.isChecked(),
            self.chk_error.isChecked(),
        )

    def refresh_devices(self, names: List[str]) -> None:
        """Refresh the sender/receiver device dropdowns."""
        self.sender_combo.clear()
        self.receiver_combo.clear()
        self.sender_combo.addItems(names)
        recv = list(names)
        recv.append(BROADCAST_RECEIVER)
        self.receiver_combo.addItems(recv)


class FlowControlPanel(QWidget):
    """Panel providing Go-Back-N and Selective Repeat controls."""

    flow_requested = pyqtSignal(str, list, int, int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Protocol"))
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["Go-Back-N", "Selective Repeat"])
        row1.addWidget(self.protocol_combo)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Frames (comma separated)"))
        self.frames_input = QLineEdit()
        row2.addWidget(self.frames_input)
        layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Window"))
        self.window_spin = QSpinBox()
        self.window_spin.setRange(1, 8)
        self.window_spin.setValue(4)
        row3.addWidget(self.window_spin)
        row3.addWidget(QLabel("Error at seq"))
        self.error_spin = QSpinBox()
        self.error_spin.setRange(-1, 100)
        self.error_spin.setValue(-1)
        row3.addWidget(self.error_spin)
        self.btn_run = QPushButton("Run flow control")
        row3.addWidget(self.btn_run)
        layout.addLayout(row3)

        self.btn_run.clicked.connect(self._emit_flow)

    def _emit_flow(self) -> None:
        """Emit the flow_requested signal based on current input."""
        frames = [s.strip() for s in self.frames_input.text().split(",") if s.strip()]
        self.flow_requested.emit(
            self.protocol_combo.currentText(),
            frames,
            self.window_spin.value(),
            self.error_spin.value(),
        )


class CRCDemoPanel(QWidget):
    """Small panel to demonstrate CRC attach/verify/corruption on raw binary input."""

    crc_demo_clicked = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Raw binary (0/1 only, spaces allowed)"))
        self.binary_input = QLineEdit()
        self.binary_input.setPlaceholderText("e.g. 11010011101100")
        layout.addWidget(self.binary_input)
        self.btn_crc = QPushButton("Compute & Verify CRC")
        layout.addWidget(self.btn_crc)
        self.crc_output = QTextEdit()
        self.crc_output.setReadOnly(True)
        layout.addWidget(self.crc_output)
        self.btn_crc.clicked.connect(self.crc_demo_clicked.emit)

    def set_crc_result(self, text: str) -> None:
        """Display CRC demo output text."""
        self.crc_output.setPlainText(text)


class StatsPanel(QWidget):
    """Panel that displays domain and MAC table reports."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        domain_group = QGroupBox("Domain report")
        domain_layout = QVBoxLayout(domain_group)
        self.domain_text = QTextEdit()
        self.domain_text.setReadOnly(True)
        domain_layout.addWidget(self.domain_text)

        mac_group = QGroupBox("MAC table")
        mac_layout = QVBoxLayout(mac_group)
        self.mac_text = QTextEdit()
        self.mac_text.setReadOnly(True)
        mac_layout.addWidget(self.mac_text)

        layout.addWidget(domain_group)
        layout.addWidget(mac_group)
        self.setLayout(layout)

    def show_domain_report(self, text: str) -> None:
        """Display the given domain report text."""
        self.domain_text.setPlainText(text)

    def show_mac_table(self, text: str) -> None:
        """Display the given MAC table report text."""
        self.mac_text.setPlainText(text)

