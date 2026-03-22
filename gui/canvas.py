from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sin
from typing import List, Tuple, Optional

from PyQt5.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QFont
from PyQt5.QtWidgets import QWidget

from gui.theme import Theme


@dataclass
class NetworkNode:
    """Represents a node drawn on the topology canvas."""

    name: str
    device_type: str
    x: float
    y: float
    selected: bool = False

    SIZE: int = 54

    def rect(self) -> QRectF:
        """Return the bounding rectangle of the circular node."""
        r = self.SIZE / 2
        return QRectF(self.x - r, self.y - r, self.SIZE, self.SIZE)

    def contains(self, x: float, y: float) -> bool:
        """Return True if the given point lies inside the node circle."""
        dx = x - self.x
        dy = y - self.y
        return dx * dx + dy * dy <= (self.SIZE / 2) ** 2

    def _colour(self) -> QColor:
        if self.selected:
            return Theme.NODE_SELECTED
        if self.device_type == "enddevice":
            return Theme.NODE_ENDDEVICE
        if self.device_type == "hub":
            return Theme.NODE_HUB
        if self.device_type == "switch":
            return Theme.NODE_SWITCH
        if self.device_type == "bridge":
            return Theme.NODE_BRIDGE
        return QColor("gray")

    def _icon_text(self) -> str:
        mapping = {
            "enddevice": "PC",
            "hub": "HUB",
            "switch": "SW",
            "bridge": "BR",
        }
        return mapping.get(self.device_type, "?")

    def draw(self, painter: QPainter) -> None:
        """Draw the node using the given painter."""
        rect = self.rect()
        # Shadow
        painter.save()
        painter.setOpacity(0.3)
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.setPen(Qt.NoPen)
        shadow_rect = QRectF(rect)
        shadow_rect.translate(3, 3)
        painter.drawEllipse(shadow_rect)
        painter.restore()

        # Body
        colour = self._colour()
        darker = QColor(colour).darker(120)
        painter.setBrush(QBrush(colour))
        painter.setPen(QPen(darker, 2))
        painter.drawEllipse(rect)

        # Icon
        painter.setPen(Qt.white)
        font = QFont("Consolas", 8, QFont.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, self._icon_text())

        # Name label
        name_rect = QRectF(rect)
        name_rect.translate(0, rect.height() / 2 + 4)
        painter.setPen(QPen(QColor("#333333")))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(name_rect, Qt.AlignHCenter | Qt.AlignTop, self.name)


class TopologyCanvas(QWidget):
    """Canvas widget that displays the network topology."""

    node_selected = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.nodes: List[NetworkNode] = []
        self.edges: List[Tuple[str, str]] = []
        self._dragging: Optional[NetworkNode] = None
        self.setMinimumSize(400, 300)
        self.setAutoFillBackground(True)

    def add_node(self, name: str, device_type: str) -> None:
        """Add a node to the canvas, auto-positioned in a circle layout."""
        count = len(self.nodes)
        radius = min(self.width(), self.height()) / 2.5 or 120
        angle = 2 * pi * (count / max(count + 1, 1))
        cx = self.width() / 2 + radius * cos(angle)
        cy = self.height() / 2 + radius * sin(angle)
        self.nodes.append(NetworkNode(name=name, device_type=device_type, x=cx, y=cy))
        self.update()

    def add_edge(self, a: str, b: str) -> None:
        """Add an undirected edge between two nodes."""
        if (a, b) not in self.edges and (b, a) not in self.edges:
            self.edges.append((a, b))
            self.update()

    def clear_all(self) -> None:
        """Remove all nodes and edges from the canvas."""
        self.nodes.clear()
        self.edges.clear()
        self._dragging = None
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.fillRect(self.rect(), Theme.BACKGROUND)

        # Grid
        painter.setPen(QPen(Theme.GRID, 1))
        step = 24
        for x in range(0, self.width(), step):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), step):
            painter.drawLine(0, y, self.width(), y)

        # Edges
        painter.setPen(QPen(Theme.LINK, 2))
        for a, b in self.edges:
            na = next((n for n in self.nodes if n.name == a), None)
            nb = next((n for n in self.nodes if n.name == b), None)
            if na and nb:
                painter.drawLine(QPointF(na.x, na.y), QPointF(nb.x, nb.y))

        # Nodes
        for node in self.nodes:
            node.draw(painter)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() != Qt.LeftButton:
            return
        x, y = event.x(), event.y()
        for node in reversed(self.nodes):
            if node.contains(x, y):
                for n in self.nodes:
                    n.selected = False
                node.selected = True
                self._dragging = node
                self.node_selected.emit(node.name)
                self.update()
                break

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._dragging is None:
            return
        self._dragging.x = event.x()
        self._dragging.y = event.y()
        self.update()

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        self._dragging = None

