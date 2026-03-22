from __future__ import annotations

from PyQt5.QtGui import QFont, QColor


class Theme:
    """Centralises colours and fonts used by the GUI."""

    BACKGROUND = QColor("#F8F8F6")
    GRID = QColor("#E8E6DF")
    LINK = QColor("#888780")

    NODE_ENDDEVICE = QColor("#378ADD")
    NODE_HUB = QColor("#1D9E75")
    NODE_SWITCH = QColor("#7F77DD")
    NODE_BRIDGE = QColor("#D85A30")
    NODE_SELECTED = QColor("#EF9F27")

    LOG_SEND = "#185FA5"
    LOG_RECV = "#0F6E56"
    LOG_COLLISION = "#993C1D"
    LOG_ERROR = "#A32D2D"
    LOG_LEARN = "#534AB7"
    LOG_INFO = "#5F5E5A"

    @staticmethod
    def code_font(size: int = 9) -> QFont:
        """Return a monospace font for logs.

        Args:
            size: Point size of the font.

        Returns:
            QFont: Configured code font.
        """
        font = QFont("Consolas")
        font.setPointSize(size)
        return font

