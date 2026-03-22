from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from physical.frame import Frame


class NetworkDevice(ABC):
    """Abstract base class for all network devices.

    Attributes:
        name: Human-readable device name.
        device_type: High-level type string (enddevice, hub, switch, bridge).
    """

    def __init__(self, name: str, device_type: str) -> None:
        """Initialise the common network device state.

        Args:
            name: Device name, unique within the simulator.
            device_type: Device type identifier.
        """
        self.name = name
        self.device_type = device_type

    @abstractmethod
    def receive_frame(self, frame: Frame) -> None:
        """Handle an incoming frame delivered to the device.

        Args:
            frame: Frame received on one of the device's ports.
        """

    @abstractmethod
    def get_collision_domains(self) -> int:
        """Return the number of collision domains associated with this device.

        Returns:
            int: Collision domain count contribution.
        """

    @abstractmethod
    def get_broadcast_domains(self) -> int:
        """Return the number of broadcast domains associated with this device.

        Returns:
            int: Broadcast domain count contribution.
        """

    def __repr__(self) -> str:
        """Return a debug representation of the device.

        Returns:
            str: String containing device name and type.
        """
        return f"{self.__class__.__name__}(name={self.name!r}, type={self.device_type!r})"


class Layer1Device(NetworkDevice, ABC):
    """Abstract base class for physical-layer devices."""

    def __init__(self, name: str, device_type: str) -> None:
        """Initialise the layer-1 device.

        Args:
            name: Device name.
            device_type: High-level type string.
        """
        super().__init__(name=name, device_type=device_type)


class Layer2Device(NetworkDevice, ABC):
    """Abstract base class for data-link-layer devices."""

    def __init__(self, name: str, device_type: str) -> None:
        """Initialise the layer-2 device.

        Args:
            name: Device name.
            device_type: High-level type string.
        """
        super().__init__(name=name, device_type=device_type)


class FlowControlProtocol(ABC):
    """Abstract base class for flow-control protocols.

    Implementations encapsulate the algorithms for Go-Back-N and
    Selective Repeat over an abstract list of frames.
    """

    @abstractmethod
    def send(self, frames: List[str], error_at: int) -> bool:
        """Run the flow-control algorithm over the provided frames.

        Args:
            frames: Ordered list of frame payload identifiers.
            error_at: Index of the frame at which to inject an error, or -1.

        Returns:
            bool: True if the algorithm completed without fatal error.
        """

