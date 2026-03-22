from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any

from core.devices import Layer2Device
from core.dispatch import relay_frame
from core.network_state import NetworkState
from physical.frame import Frame


@dataclass
class Switch(Layer2Device):
    """Represents a layer-2 switch with a learning MAC table."""

    mac_table: Dict[str, Any] = field(default_factory=dict)
    ports: List[Any] = field(default_factory=list)

    def __init__(self, name: str) -> None:
        """Initialise the switch with an empty MAC table and ports."""
        Layer2Device.__init__(self, name=name, device_type="switch")
        self.mac_table = {}
        self.ports = []

    def connect(self, device: Any) -> None:
        """Connect an arbitrary device to one of the switch ports.

        Args:
            device: Device to connect.
        """
        self.ports.append(device)

    def _learn(self, mac: str, device: Any) -> None:
        """Learn the source MAC to port mapping.

        Args:
            mac: Source MAC address.
            device: Device through which the MAC was observed.
        """
        state = NetworkState.get_instance()
        if mac not in self.mac_table:
            self.mac_table[mac] = device
            state.log("learn", f"learned {mac} -> port of {getattr(device, 'name', '?')}")

    def _flood(self, frame: Frame, source: Any) -> None:
        """Flood the frame to all ports except the source.

        Args:
            frame: Frame to flood.
            source: Source device.
        """
        for dev in self.ports:
            if dev is not source:
                relay_frame(dev, frame, self)

    def _unicast(self, frame: Frame) -> None:
        """Unicast the frame to the specific learned destination port.

        Args:
            frame: Frame to forward.
        """
        dest = self.mac_table.get(frame.receiver_mac)
        if dest is not None:
            NetworkState.get_instance().log(
                "send",
                f"unicast to {getattr(dest, 'name', '?')}",
            )
            relay_frame(dest, frame, self)

    def receive_frame(self, frame: Frame, source: Any) -> None:  # type: ignore[override]
        """Receive a frame from a port and forward it according to MAC table.

        Args:
            frame: Frame received.
            source: Port device where the frame arrived.
        """
        self._learn(frame.sender_mac, source)
        if frame.is_broadcast():
            self._flood(frame, source)
        elif frame.receiver_mac in self.mac_table:
            self._unicast(frame)
        else:
            NetworkState.get_instance().log("info", "unknown dest, flooding")
            self._flood(frame, source)

    def get_collision_domains(self) -> int:
        """Return the collision domain count contributed by this switch.

        Returns:
            int: Equal to the number of ports.
        """
        return len(self.ports)

    def get_broadcast_domains(self) -> int:
        """Return the broadcast domain count contributed by this switch.

        Returns:
            int: Always 1 for a switch.
        """
        return 1

    def get_mac_table_display(self) -> str:
        """Return a human-readable representation of the MAC table.

        Returns:
            str: MAC address to device name mapping lines.
        """
        lines = []
        for mac, dev in self.mac_table.items():
            lines.append(f"{mac} -> {getattr(dev, 'name', '?')}")
        return "\n".join(lines)

