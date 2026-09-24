"""Position sizing + loss limits. Pure functions — easy to test, hard to break."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskConfig:
    max_daily_loss: float = 5000.0
    max_position_qty: int = 200
    risk_per_trade_pct: float = 1.0  # % of capital risked per trade


def position_qty(capital: float, risk_per_trade_pct: float, stop_loss_per_unit: float) -> int:
    """Fixed-fractional size: risk a % of capital, divide by stop per unit."""
    if stop_loss_per_unit <= 0:
        raise ValueError("stop_loss_per_unit must be positive")
    risk_amount = capital * (risk_per_trade_pct / 100.0)
    return max(0, int(risk_amount // stop_loss_per_unit))


def check_order(qty: int, day_pnl: float, kill_engaged: bool, cfg: RiskConfig) -> tuple[bool, str]:
    """Gate every order. Returns (allowed, reason)."""
    if kill_engaged:
        return False, "kill switch engaged — flatten and stop"
    if qty <= 0:
        return False, "qty must be positive"
    if qty > cfg.max_position_qty:
        return False, f"qty {qty} exceeds max_position_qty {cfg.max_position_qty}"
    if day_pnl <= -cfg.max_daily_loss:
        return False, f"daily loss limit hit ({day_pnl:.2f} <= -{cfg.max_daily_loss:.2f})"
    return True, "ok"
