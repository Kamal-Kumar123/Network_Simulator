from __future__ import annotations

import random
from typing import ClassVar


class CRC:
    """Implements a simple CRC generator/checker with polynomial 1101.

    All methods are class or static methods so the algorithm can be
    demonstrated without instantiating the class.
    """

    DIVISOR: ClassVar[str] = "1101"

    @classmethod
    def attach(cls, binary_data: str) -> str:
        """Append CRC remainder bits to the given binary string.

        Args:
            binary_data: Original binary payload (no CRC bits).

        Returns:
            str: Payload with CRC bits appended.
        """
        divisor = cls.DIVISOR
        padded = binary_data + "0" * (len(divisor) - 1)
        result = cls._xor_divide(padded, divisor)
        remainder = result[-(len(divisor) - 1) :]
        return binary_data + remainder

    @classmethod
    def verify(cls, received: str) -> bool:
        """Verify whether the received frame has a valid CRC.

        Args:
            received: Full bit string including CRC bits.

        Returns:
            bool: True if the remainder is all zeros.
        """
        remainder = cls._xor_divide(received, cls.DIVISOR)
        return all(bit == "0" for bit in remainder[-(len(cls.DIVISOR) - 1) :])

    @classmethod
    def introduce_error(cls, frame: str) -> str:
        """Flip a random bit in the frame for error demonstration.

        Args:
            frame: Original bit string.

        Returns:
            str: Bit string with one randomly flipped bit.
        """
        if not frame:
            return frame
        pos = random.randrange(len(frame))
        flipped = "1" if frame[pos] == "0" else "0"
        return frame[:pos] + flipped + frame[pos + 1 :]

    @staticmethod
    def _xor_divide(dividend: str, divisor: str) -> str:
        """Perform polynomial long division using XOR.

        Args:
            dividend: Dividend bit string.
            divisor: Divisor bit string.

        Returns:
            str: Resulting bit string after division.
        """
        dividend_list = list(dividend)
        for i in range(len(dividend) - len(divisor) + 1):
            if dividend_list[i] == "1":
                for j in range(len(divisor)):
                    dividend_list[i + j] = (
                        "0" if dividend_list[i + j] == divisor[j] else "1"
                    )
        return "".join(dividend_list)

