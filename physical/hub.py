from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List

from core.devices import Layer1Device
from core.dispatch import relay_frame
from core.network_state import NetworkState
from physical.frame import Frame


@dataclass
class Hub(Layer1Device):
    """Represents a physical-layer hub using shared collision/broadcast domain.

    The hub simply repeats incoming frames out of all other ports.
    """

    ports: List[Any] = field(default_factory=list)

    def __init__(self, name: str) -> None:
        """Initialise the hub with no connected ports.

        Args:
            name: Name of the hub.
        """
        Layer1Device.__init__(self, name=name, device_type="hub")
        self.ports = []

    def connect(self, device: Any) -> None:
        """Attach an end device or uplink (e.g. switch) to one of the hub's ports.

        Args:
            device: Device connected to this hub port.
        """
        self.ports.append(device)

    def broadcast(self, frame: Frame, source: Any) -> None:
        """Broadcast a frame to all ports except the source.

        Args:
            frame: Frame to broadcast.
            source: Device on whose port the frame arrived.
        """
        state = NetworkState.get_instance()
        state.log("info", f"Hub {self.name} broadcasting frame from {getattr(source, 'name', '?')}")
        for dev in self.ports:
            if dev is not source:
                relay_frame(dev, frame, self)

    def receive_frame(self, frame: Frame, source: Any) -> None:  # type: ignore[override]
        """Receive a frame on one port and broadcast it.

        Args:
            frame: Frame received.
            source: Device on whose port the frame arrived.
        """
        state = NetworkState.get_instance()
        state.log("send", f"Hub {self.name} repeating frame from {source.name}")
        self.broadcast(frame, source)

    def get_collision_domains(self) -> int:
        """Return the number of collision domains the hub participates in.

        Returns:
            int: Always 1 for a hub.
        """
        return 1

    def get_broadcast_domains(self) -> int:
        """Return the number of broadcast domains the hub participates in.

        Returns:
            int: Always 1 for a hub.
        """
        return 1

