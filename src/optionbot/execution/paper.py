"""Paper trading: simulated fills against live NSE quotes. No real money.

Every order passes the risk gate first. Fills are logged with price/qty so a
later backtester can replay them exactly.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..data.kite import Order
from ..logging_setup import log
from ..risk.kill_switch import KillSwitch
from ..risk.limits import RiskConfig, check_order


@dataclass
class Fill:
    order: Order
    fill_price: float
    status: str = "filled"


@dataclass
class PaperPortfolio:
    capital: float = 100000.0
    positions: list = field(default_factory=list)
    fills: list = field(default_factory=list)
    realized_pnl: float = 0.0
    cfg: RiskConfig = field(default_factory=RiskConfig)
    kill: KillSwitch = field(default_factory=KillSwitch)

    @property
    def day_pnl(self) -> float:
        return self.realized_pnl

    def buy(self, symbol: str, strike: float, option_type: str, qty: int, price: float) -> Fill:
        allowed, reason = check_order(qty, self.day_pnl, self.kill.engaged, self.cfg)
        if not allowed:
            log.warning("order blocked: %s", reason)
            raise RuntimeError(f"order blocked: {reason}")
        cost = price * qty
        if cost > self.capital:
            raise RuntimeError(f"insufficient capital ({self.capital:.2f} < {cost:.2f})")
        order = Order(symbol, strike, option_type, qty, price)
        self.capital -= cost
        self.positions.append({"symbol": symbol, "strike": strike, "type": option_type,
                               "qty": qty, "entry": price})
        fill = Fill(order, price)
        self.fills.append(fill)
        log.info("paper BUY %s %s %s x%d @ %.2f", symbol, strike, option_type, qty, price)
        return fill

    def mark_to_market(self, current_prices: dict) -> float:
        """Value open positions at `current_prices[(strike, type)]`. Returns unrealized P&L."""
        upl = 0.0
        for p in self.positions:
            cur = current_prices.get((p["strike"], p["type"]), p["entry"])
            upl += (cur - p["entry"]) * p["qty"]
        return upl

    def summary(self) -> dict:
        return {"capital": round(self.capital, 2), "open_positions": len(self.positions),
                "fills": len(self.fills), "realized_pnl": round(self.realized_pnl, 2)}
