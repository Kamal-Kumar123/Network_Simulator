from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.devices import FlowControlProtocol
from core.network_state import NetworkState


@dataclass
class GoBackN(FlowControlProtocol):
    """Implements the Go-Back-N sliding window ARQ algorithm."""

    window_size: int

    def send(self, frames: List[str], error_at: int) -> bool:
        """Run the Go-Back-N algorithm for the given frames.

        Args:
            frames: List of frame payloads.
            error_at: Index of the frame at which to inject an error, or -1.

        Returns:
            bool: True when all frames are acknowledged.
        """
        state = NetworkState.get_instance()
        base = 0
        while base < len(frames):
            window = frames[base : base + self.window_size]
            state.log(
                "info",
                f"GBN window: frames {base}..{base + len(window) - 1}",
            )
            for seq in range(base, base + len(window)):
                state.log("send", f"Frame {seq}: '{frames[seq]}'")
                if seq == error_at:
                    state.log(
                        "error",
                        f"Frame {seq} LOST - NAK, going back to {seq}",
                    )
                    base = seq
                    error_at = -1
                    break
            else:
                state.log(
                    "recv",
                    f"ACK for frames {base}..{base + len(window) - 1}",
                )
                base += len(window)
        state.log("info", "All frames acknowledged")
        return True


@dataclass
class SelectiveRepeat(FlowControlProtocol):
    """Implements the Selective Repeat sliding window ARQ algorithm."""

    window_size: int

    def send(self, frames: List[str], error_at: int) -> bool:
        """Run the Selective Repeat algorithm for the given frames.

        Args:
            frames: List of frame payloads.
            error_at: Index of the frame at which to inject an error, or -1.

        Returns:
            bool: True when all frames are acknowledged.
        """
        state = NetworkState.get_instance()
        acked = [False] * len(frames)
        base = 0
        while base < len(frames):
            for seq in range(base, min(base + self.window_size, len(frames))):
                if acked[seq]:
                    continue
                state.log("send", f"Sending frame {seq}: '{frames[seq]}'")
                if seq == error_at:
                    state.log(
                        "error",
                        f"Frame {seq} LOST - selective retransmit",
                    )
                    error_at = -1
                    state.log("send", f"[RTX] Retransmitting frame {seq} only")
                acked[seq] = True
                state.log("recv", f"ACK {seq}")
            while base < len(frames) and acked[base]:
                base += 1
        state.log("info", "All frames acknowledged")
        return True

