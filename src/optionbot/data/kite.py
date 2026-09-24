"""Broker interface. Kite Connect wiring lands in Phase 4.

Everything trades through `Broker` so paper mode (default) and live mode are
interchangeable. Live methods raise until API credentials are configured —
never fail open into real orders.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Order:
    symbol: str
    strike: float
    option_type: str  # "CE" | "PE"
    qty: int
    price: float
    side: str = "BUY"


class Broker:
    name = "base"

    def place_order(self, order: Order) -> dict:
        raise NotImplementedError


class KiteBroker(Broker):
    """Zerodha Kite Connect. Stub until KITE_* env vars are set (Phase 4)."""

    name = "kite"

    def __init__(self, api_key: str = "", access_token: str = ""):
        self.api_key = api_key
        self.access_token = access_token

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.access_token)

    def place_order(self, order: Order) -> dict:
        if not self.configured:
            raise RuntimeError("KiteBroker not configured — set KITE_API_KEY / KITE_ACCESS_TOKEN (Phase 4)")
        raise NotImplementedError("live execution arrives in Phase 4")
