"""Frame delivery helpers (lazy imports avoid circular dependencies)."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from physical.frame import Frame


def relay_frame(device: Any, frame: "Frame", arrived_from: Any) -> None:
    """Deliver a frame using the correct ``receive_frame`` signature for *device*.

    End devices use ``receive_frame(frame)``. Hubs, switches, and bridges use
    ``receive_frame(frame, source)`` where *source* is the immediate neighbor.

    Args:
        device: Target device.
        frame: Frame to deliver.
        arrived_from: Neighbor that forwarded the frame toward *device*.
    """
    from datalink.bridge import Bridge
    from datalink.switch import Switch
    from physical.end_device import EndDevice
    from physical.hub import Hub

    if isinstance(device, EndDevice):
        device.receive_frame(frame)
    elif isinstance(device, Hub):
        device.receive_frame(frame, arrived_from)
    elif isinstance(device, Switch):
        device.receive_frame(frame, arrived_from)
    elif isinstance(device, Bridge):
        device.receive_frame(frame, arrived_from)
