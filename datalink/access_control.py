from __future__ import annotations

import random
import time
from dataclasses import dataclass

from core.network_state import NetworkState
from physical.frame import Frame


@dataclass
class CSMACD:
    """Implements a simple CSMA/CD access control mechanism.

    Attributes:
        channel_busy: Flag indicating whether the channel is currently busy.
        MAX_ATTEMPTS: Maximum number of retransmission attempts.
        COLLISION_PROB: Probability of a collision on each attempt.
    """

    channel_busy: bool = False
    MAX_ATTEMPTS: int = 16
    COLLISION_PROB: float = 0.25

    def transmit(self, sender_name: str, frame: Frame) -> bool:
        """Attempt to transmit a frame using CSMA/CD.

        Args:
            sender_name: Name of the sending device.
            frame: Frame to be transmitted.

        Returns:
            bool: True if transmitted successfully, False on failure.
        """
        state = NetworkState.get_instance()
        for attempt in range(self.MAX_ATTEMPTS):
            if self.channel_busy:
                state.log("info", "channel busy, waiting...")
                time.sleep(0.05)
                continue
            self.channel_busy = True
            if random.random() < self.COLLISION_PROB and attempt < 5:
                state.collision_count += 1
                slots = random.randint(0, (2 ** min(attempt + 1, 10)) - 1)
                state.log(
                    "collision",
                    f"COLLISION #{state.collision_count}, backoff {slots} slots",
                )
                self.channel_busy = False
                time.sleep(slots * 0.01)
                continue
            state.log("send", f"transmitted successfully (attempt {attempt + 1})")
            self.channel_busy = False
            return True
        state.log("error", "gave up after 16 attempts")
        return False

