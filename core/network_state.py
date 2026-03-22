from __future__ import annotations

from dataclasses import dataclass
from time import time
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class EventLog:
    """Represents a single simulator log entry.

    Attributes:
        timestamp: Unix timestamp when the event occurred.
        level: Logical event level (send, recv, collision, error, learn, info).
        message: Human-readable description of what happened.
    """

    timestamp: float
    level: str
    message: str


class NetworkState:
    """Singleton shared state for the entire network simulator.

    This class tracks devices, connections, MAC learning, collisions, and
    a chronological list of high-level protocol events. GUI components
    subscribe via callbacks to receive new log entries.
    """

    _instance: Optional["NetworkState"] = None

    def __init__(self) -> None:
        """Initialise an empty network state."""
        self.devices: Dict[str, Any] = {}
        self.connections: List[Tuple[str, str]] = []
        self.events: List[EventLog] = []
        self.mac_table: Dict[str, str] = {}
        self.collision_count: int = 0
        self._listeners: List[Callable[[EventLog], None]] = []

    @classmethod
    def get_instance(cls) -> "NetworkState":
        """Return the global NetworkState singleton instance.

        Returns:
            NetworkState: The shared singleton instance.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def log(self, level: str, message: str) -> None:
        """Append an event to the log and notify listeners.

        Args:
            level: Logical level of the event (send, recv, collision, error, learn, info).
            message: Human-readable message to record.
        """
        entry = EventLog(timestamp=time(), level=level, message=message)
        self.events.append(entry)
        for cb in list(self._listeners):
            cb(entry)

    def on_event(self, callback: Callable[[EventLog], None]) -> None:
        """Register a listener for new log events.

        Args:
            callback: Function invoked with each new EventLog.
        """
        self._listeners.append(callback)

    def clear(self) -> None:
        """Reset all state, removing devices, connections, and events."""
        self.devices.clear()
        self.connections.clear()
        self.events.clear()
        self.mac_table.clear()
        self.collision_count = 0
