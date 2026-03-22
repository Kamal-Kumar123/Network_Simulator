from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Frame:
    """Represents a simple data-link frame used in the simulator.

    Attributes:
        data: Payload string carried by the frame.
        sender_mac: MAC address of the originating end device.
        receiver_mac: Destination MAC address, or FF:FF:FF:FF:FF:FF for broadcast.
        crc: Optional CRC bits appended to the encoded payload.
        sequence_number: Optional sequence number for flow-control protocols.
    """

    data: str
    sender_mac: str
    receiver_mac: str
    crc: str | None = None
    sequence_number: int | None = None

    def to_bits(self) -> str:
        """Return the NRZ line-coded bit representation of the payload.

        Each character is encoded as eight bits using its ASCII value.

        Returns:
            str: A space-separated string of 8-bit groups.
        """
        bits = [format(ord(ch), "08b") for ch in self.data]
        return " ".join(bits)

    def is_broadcast(self) -> bool:
        """Return True if the frame is addressed to the broadcast MAC.

        Returns:
            bool: True if receiver_mac is the broadcast address.
        """
        return self.receiver_mac.upper() == "FF:FF:FF:FF:FF:FF"

    def __repr__(self) -> str:
        """Return a concise textual representation of the frame.

        Returns:
            str: Debug representation containing MAC addresses and data.
        """
        return (
            f"Frame(data='{self.data}', "
            f"{self.sender_mac}->{self.receiver_mac}, "
            f"seq={self.sequence_number}, crc={self.crc})"
        )

