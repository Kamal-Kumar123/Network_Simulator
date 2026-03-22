"""Logical link between two devices (for documentation and future extensions)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Connection:
    """Represents an undirected link between two devices in the topology.

    The simulator currently stores edges as tuples in ``NetworkState.connections``;
    this class documents the intended model for a dedicated connection object.

    Attributes:
        device_a: First endpoint device.
        device_b: Second endpoint device.
        medium: Label for the medium type (e.g. ``copper``, ``fiber``).
    """

    device_a: Any
    device_b: Any
    medium: str = "ethernet"

    def __repr__(self) -> str:
        """Return a short description of the connection.

        Returns:
            str: Human-readable connection summary.
        """
        na = getattr(self.device_a, "name", "?")
        nb = getattr(self.device_b, "name", "?")
        return f"Connection({na!s} <-> {nb!s}, medium={self.medium!r})"
