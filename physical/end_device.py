from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from core.devices import Layer1Device
from core.network_state import NetworkState
from physical.frame import Frame


@dataclass
class EndDevice(Layer1Device):
    """Represents a simple host/end device in the physical layer.

    End devices originate and terminate frames but do not forward them.
    """

    mac: str = ""  #SENDER MAC ADDRESS
    inbox: List[Frame] = field(default_factory=list)

    def __init__(self, name: str, mac: str) -> None:
        """Initialise an end device with name and MAC address.

        Args:
            name: Device name.
            mac: MAC address string.
        """
        Layer1Device.__init__(self, name=name, device_type="enddevice")
        self.mac = mac
        self.inbox = []

    def send(self, data: str, receiver_mac: str) -> Frame:
        """Create a frame to be transmitted from this end device.

        Args:
            data: Application payload to send.
            receiver_mac: Target destination MAC address.

        Returns:
            Frame: Newly created frame instance.
        """
        frame = Frame(data=data, sender_mac=self.mac, receiver_mac=receiver_mac)
        NetworkState.get_instance().log(
            "send",
            f"{self.name} [{self.mac}] sending '{data}' bits: {frame.to_bits()}",
        )
        return frame

    def receive_frame(self, frame: Frame) -> None:
        """Handle an incoming frame delivered to this device.

        Args:
            frame: Frame received from the medium.
        """
        if frame.receiver_mac == self.mac or frame.is_broadcast():
            self.inbox.append(frame)
            NetworkState.get_instance().log(
                "recv",
                f"{self.name} [{self.mac}] received '{frame.data}'",
            )

    def get_collision_domains(self) -> int:
        """Return the number of collision domains for this device.

        Returns:
            int: Always zero for end devices (they do not segment domains).
        """
        return 0

    def get_broadcast_domains(self) -> int:
        """Return the number of broadcast domains for this device.

        Returns:
            int: Always zero for end devices (they do not segment domains).
        """
        return 0

