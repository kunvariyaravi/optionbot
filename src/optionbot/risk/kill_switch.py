"""Kill switch: one flag that halts all trading. Checked before every order."""
from __future__ import annotations


class KillSwitch:
    def __init__(self) -> None:
        self._engaged = False
        self.reason = ""

    @property
    def engaged(self) -> bool:
        return self._engaged

    def engage(self, reason: str = "manual") -> None:
        self._engaged = True
        self.reason = reason

    def reset(self) -> None:
        self._engaged = False
        self.reason = ""
