from __future__ import annotations

from typing import Optional

from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QTextEdit, QWidget, QVBoxLayout

from core.network_state import EventLog
from gui.theme import Theme


class EventLogWidget(QWidget):
    """Widget that displays formatted simulator events."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.log_box = QTextEdit(self)
        self.log_box.setReadOnly(True)
        self.log_box.setFont(Theme.code_font(9))
        layout = QVBoxLayout(self)
        layout.addWidget(self.log_box)
        self.setLayout(layout)

    def append_event(self, entry: EventLog) -> None:
        """Append an EventLog entry using coloured HTML formatting."""
        colour = Theme.LOG_INFO
        symbol = "·"
        if entry.level == "send":
            colour = Theme.LOG_SEND
            symbol = "→"
        elif entry.level == "recv":
            colour = Theme.LOG_RECV
            symbol = "←"
        elif entry.level == "collision":
            colour = Theme.LOG_COLLISION
            symbol = "✗"
        elif entry.level == "error":
            colour = Theme.LOG_ERROR
            symbol = "!"
        elif entry.level == "learn":
            colour = Theme.LOG_LEARN
            symbol = "★"

        html = (
            f'<span style="color:{colour}">[{symbol} {entry.level.upper():8}] '
            f"{entry.message}</span><br/>"
        )
        self.log_box.moveCursor(QTextCursor.End)
        self.log_box.insertHtml(html)
        self.log_box.moveCursor(QTextCursor.End)

    def clear(self) -> None:
        """Clear all log contents."""
        self.log_box.clear()

