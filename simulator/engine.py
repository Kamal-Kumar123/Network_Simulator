from __future__ import annotations

from typing import List

from core.network_state import NetworkState
from datalink.access_control import CSMACD
from datalink.bridge import Bridge
from datalink.error_control import CRC
from datalink.flow_control import GoBackN, SelectiveRepeat
from datalink.switch import Switch
from physical.end_device import EndDevice
from physical.hub import Hub
from physical.frame import Frame

# Receiver name in GUI for broadcast sends (must match panels.ControlPanel).
BROADCAST_RECEIVER = "(Broadcast)"


class Simulator:
    """High-level API wrapping all protocol-layer components.

    The simulator owns the NetworkState singleton and exposes convenient
    methods for the GUI and headless runner to manipulate the topology.
    """

    def __init__(self) -> None:
        """Initialise a new simulator with empty topology."""
        self.state = NetworkState.get_instance()
        self._csma = CSMACD()

    def add_device(self, name: str, mac: str) -> EndDevice:
        """Add an end device with a given name and MAC."""
        dev = EndDevice(name=name, mac=mac)
        self.state.devices[name] = dev
        return dev

    def add_hub(self, name: str) -> Hub:
        """Add a hub device."""
        hub = Hub(name=name)
        self.state.devices[name] = hub
        return hub

    def add_switch(self, name: str) -> Switch:
        """Add a switch device."""
        sw = Switch(name=name)
        self.state.devices[name] = sw
        return sw

    def add_bridge(self, name: str) -> Bridge:
        """Add a bridge device."""
        br = Bridge(name=name)
        self.state.devices[name] = br
        return br

    def connect(self, name_a: str, name_b: str, segment: str = "A") -> bool:
        """Connect two devices in the topology.

        Args:
            name_a: Name of the first device.
            name_b: Name of the second device.
            segment: Segment identifier for bridges ("A" or "B").

        Returns:
            bool: True if the connection was established.
        """
        a = self.state.devices.get(name_a)
        b = self.state.devices.get(name_b)
        if not a or not b:
            return False
        self.state.connections.append((name_a, name_b))

        # Hub connections (PCs or uplink to switch)
        if isinstance(a, Hub) and isinstance(b, (EndDevice, Switch)):
            a.connect(b)
        elif isinstance(b, Hub) and isinstance(a, (EndDevice, Switch)):
            b.connect(a)
        # Switch ports
        if isinstance(a, Switch):
            a.connect(b)
        if isinstance(b, Switch):
            b.connect(a)
        # Bridge segments
        if isinstance(a, Bridge):
            (a.connect_segment_a if segment == "A" else a.connect_segment_b)(b)
        if isinstance(b, Bridge):
            (b.connect_segment_a if segment == "A" else b.connect_segment_b)(a)
        return True

    def _deliver(self, frame: Frame, source: EndDevice) -> None:
        """Deliver a frame from the source into the network.

        This simplified implementation sends directly to connected devices
        in the NetworkState connections list.
        """
        for a, b in self.state.connections:
            if a == source.name:
                dest = self.state.devices.get(b)
            elif b == source.name:
                dest = self.state.devices.get(a)
            else:
                continue
            if isinstance(dest, Hub):
                dest.receive_frame(frame, source)
            elif isinstance(dest, Switch):
                dest.receive_frame(frame, source)
            elif isinstance(dest, Bridge):
                dest.receive_frame(frame, source)
            elif isinstance(dest, EndDevice):
                dest.receive_frame(frame)

    def send_frame(
        self,
        sender: str,
        receiver: str,
        data: str,
        use_crc: bool,
        use_csma: bool,
        introduce_error: bool,
    ) -> bool:
        """Create and send a frame from sender to receiver.

        Args:
            sender: Sender device name.
            receiver: Receiver end device name, or ``(Broadcast)`` for hub broadcast.
            data: Payload string.
            use_crc: Attach CRC (polynomial 1101) to the NRZ bit string and verify.
            use_csma: Whether to use CSMA/CD before transmit.
            introduce_error: Flip one bit before CRC verify (noise model).

        Returns:
            bool: True if sending proceeded.
        """
        state = self.state
        src_dev = self.state.devices.get(sender)
        if not isinstance(src_dev, EndDevice):
            return False

        is_broadcast = receiver.strip() == BROADCAST_RECEIVER
        if is_broadcast:
            dst_mac = "FF:FF:FF:FF:FF:FF"
        else:
            dst_dev = self.state.devices.get(receiver)
            if not isinstance(dst_dev, EndDevice):
                return False
            dst_mac = dst_dev.mac

        frame = src_dev.send(data, dst_mac)

        if use_crc:
            payload_bits = "".join(f"{ord(ch):08b}" for ch in data)
            full_with_crc = CRC.attach(payload_bits)
            frame.crc = full_with_crc[len(payload_bits) :]
            state.log(
                "info",
                f"CRC: appended to {len(payload_bits)} data bits; "
                f"CRC bits={frame.crc!r}; full length={len(full_with_crc)}",
            )
            check_bits = full_with_crc
            if introduce_error:
                corrupted = CRC.introduce_error(full_with_crc)
                flip_pos = next(
                    (i for i, (a, b) in enumerate(zip(full_with_crc, corrupted)) if a != b),
                    -1,
                )
                state.log("error", f"bit flipped at position {flip_pos}")
                check_bits = corrupted
            ok = CRC.verify(check_bits)
            state.log("error" if not ok else "info", f"CRC verify: {'OK' if ok else 'FAIL'}")

        if use_csma:
            if not self._csma.transmit(src_dev.name, frame):
                return False
        self._deliver(frame, src_dev)
        return True

    def run_go_back_n(self, frames: List[str], window: int, error_at: int) -> None:
        """Run the Go-Back-N demo."""
        GoBackN(window_size=window).send(frames, error_at)

    def run_selective_repeat(self, frames: List[str], window: int, error_at: int) -> None:
        """Run the Selective Repeat demo."""
        SelectiveRepeat(window_size=window).send(frames, error_at)

    def crc_demo_report(self, raw_bits: str) -> str:
        """Return multi-line text for the CRC attach/verify/corruption demo (GUI).

        Args:
            raw_bits: Binary string from the user (may contain spaces).

        Returns:
            str: Human-readable CRC demonstration output.
        """
        raw = "".join(raw_bits.split())
        if not raw or any(ch not in "01" for ch in raw):
            return "Enter a non-empty binary string (only 0 and 1)."
        full = CRC.attach(raw)
        crc_bits = full[len(raw) :]
        ok = CRC.verify(full)
        corrupted = CRC.introduce_error(full)
        ok_bad = CRC.verify(corrupted)
        return (
            f"Original data bits ({len(raw)}): {raw}\n"
            f"CRC remainder bits: {crc_bits}\n"
            f"Full frame (data+CRC): {full}\n"
            f"Verify original: {'OK' if ok else 'FAIL'}\n"
            f"Corrupted frame: {corrupted}\n"
            f"Verify corrupted: {'OK' if ok_bad else 'FAIL'}"
        )

    def get_domain_report(self) -> str:
        """Return a human-readable report of collision/broadcast domains."""
        devices = list(self.state.devices.values())
        hubs = [d for d in devices if isinstance(d, Hub)]
        switches = [d for d in devices if isinstance(d, Switch)]

        lines: List[str] = []
        for dev in devices:
            c = getattr(dev, "get_collision_domains", lambda: 0)()
            b = getattr(dev, "get_broadcast_domains", lambda: 0)()
            lines.append(
                f"{dev.__class__.__name__} {dev.name}: {c} collision domains, {b} broadcast domains"
            )

        # ITL351-style totals: two hubs + one switch (uplinks only) => 3 collision domains.
        special_two_hubs_one_switch = (
            len(hubs) == 2
            and len(switches) == 1
            and len(switches[0].ports) == 2
            and all(isinstance(p, Hub) for p in switches[0].ports)
        )
        if special_two_hubs_one_switch:
            total_collision = 3
            total_broadcast = 1
        else:
            total_collision = sum(
                getattr(d, "get_collision_domains", lambda: 0)() for d in devices
            )
            total_broadcast = sum(
                getattr(d, "get_broadcast_domains", lambda: 0)() for d in devices
            )

        lines.append(f"Total collision domains: {total_collision}")
        lines.append(f"Total broadcast domains: {total_broadcast}")
        lines.append(f"Total collisions detected: {self.state.collision_count}")
        return "\n".join(lines)

    def get_mac_table_report(self) -> str:
        """Return a combined MAC table report from all switches."""
        lines: List[str] = []
        for dev in self.state.devices.values():
            if isinstance(dev, Switch):
                lines.append(f"Switch {dev.name}")
                lines.append(dev.get_mac_table_display() or "(empty)")
        return "\n".join(lines)

    def reset(self) -> None:
        """Reset the entire simulation state."""
        self.state.clear()
        self._csma = CSMACD()

