from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from core.devices import Layer2Device
from core.dispatch import relay_frame
from core.network_state import NetworkState
from physical.frame import Frame


@dataclass
class Bridge(Layer2Device):
    """Represents a transparent bridge connecting two collision domains."""

    segment_a: List[Any] = field(default_factory=list)
    segment_b: List[Any] = field(default_factory=list)
    mac_table_a: Dict[str, Any] = field(default_factory=dict)
    mac_table_b: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, name: str) -> None:
        """Initialise the bridge with two empty segments."""
        Layer2Device.__init__(self, name=name, device_type="bridge")
        self.segment_a = []
        self.segment_b = []
        self.mac_table_a = {}
        self.mac_table_b = {}

    def connect_segment_a(self, device: Any) -> None:
        """Connect a device to segment A.

        Args:
            device: Device to add to segment A.
        """
        self.segment_a.append(device)

    def connect_segment_b(self, device: Any) -> None:
        """Connect a device to segment B.

        Args:
            device: Device to add to segment B.
        """
        self.segment_b.append(device)

    def _learn(self, frame: Frame, source: Any) -> None:
        """Learn MAC locations on each segment based on the source.

        Args:
            frame: Frame carrying the source MAC.
            source: Device on which the frame was seen.
        """
        state = NetworkState.get_instance()
        if source in self.segment_a and frame.sender_mac not in self.mac_table_a:
            self.mac_table_a[frame.sender_mac] = source
            state.log("learn", f"learned {frame.sender_mac} on segment A")
        if source in self.segment_b and frame.sender_mac not in self.mac_table_b:
            self.mac_table_b[frame.sender_mac] = source
            state.log("learn", f"learned {frame.sender_mac} on segment B")

    def receive_frame(self, frame: Frame, source: Any) -> None:  # type: ignore[override]
        """Receive a frame from a segment and decide whether to forward.

        Args:
            frame: Frame received.
            source: Device that sent the frame towards the bridge.
        """
        self._learn(frame, source)
        state = NetworkState.get_instance()

        if source in self.segment_a:
            if frame.receiver_mac in self.mac_table_a or frame.is_broadcast():
                state.log("info", "filtering frame on same segment A")
                for dev in self.segment_a:
                    if dev is not source:
                        relay_frame(dev, frame, self)
            else:
                state.log("send", "forwarding frame from A to B")
                for dev in self.segment_b:
                    relay_frame(dev, frame, self)
        elif source in self.segment_b:
            if frame.receiver_mac in self.mac_table_b or frame.is_broadcast():
                state.log("info", "filtering frame on same segment B")
                for dev in self.segment_b:
                    if dev is not source:
                        relay_frame(dev, frame, self)
            else:
                state.log("send", "forwarding frame from B to A")
                for dev in self.segment_a:
                    relay_frame(dev, frame, self)

    def get_collision_domains(self) -> int:
        """Return the number of collision domains contributed by the bridge.

        Returns:
            int: Always 2 for a bridge.
        """
        return 2

    def get_broadcast_domains(self) -> int:
        """Return the number of broadcast domains contributed by the bridge.

        Returns:
            int: Always 1 for a bridge.
        """
        return 1

