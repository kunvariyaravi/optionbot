"""CLI: `python -m optionbot.cli fetch-chain | paper`. No server needed."""
from __future__ import annotations

import argparse
import json

from .config import settings
from .data.nse import atm_strike, fetch_chain
from .execution.paper import PaperPortfolio
from .logging_setup import log
from .risk.kill_switch import KillSwitch
from .risk.limits import RiskConfig


def cmd_fetch_chain(args: argparse.Namespace) -> None:
    data = fetch_chain(args.symbol)
    row = atm_strike(data)
    print(json.dumps({"symbol": args.symbol.upper(), "underlying": row["underlying"],
                      "atm_strike": row["strike"], "ce_ltp": row["CE"].get("lastPrice"),
                      "pe_ltp": row["PE"].get("lastPrice"),
                      "nearest_expiry": data["records"]["expiryDates"][0]}, indent=2))


def cmd_paper(args: argparse.Namespace) -> None:
    """Demo paper trade: buy one ATM CE at live LTP through the risk gate."""
    if getattr(settings, "KILL_SWITCH", False):
        kill = KillSwitch()
        kill.engage("KILL_SWITCH=true in env")
    else:
        kill = KillSwitch()
    cfg = RiskConfig(max_daily_loss=args.max_loss, max_position_qty=args.max_qty)
    pf = PaperPortfolio(capital=args.capital, cfg=cfg, kill=kill)
    row = atm_strike(fetch_chain(args.symbol))
    ltp = float(row["CE"].get("lastPrice") or 0)
    if ltp <= 0:
        raise SystemExit("no live CE price — market may be closed")
    pf.buy(args.symbol.upper(), row["strike"], "CE", args.qty, ltp)
    print(json.dumps({**pf.summary(), "atm": row["strike"], "entry_ltp": ltp}, indent=2))
    log.info("paper position open — track it at GET /portfolio")


def main() -> None:
    p = argparse.ArgumentParser(prog="optionbot", description="NSE options paper-trading bot")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch-chain", help="print ATM snapshot for a symbol")
    f.add_argument("--symbol", default="NIFTY")
    f.set_defaults(fn=cmd_fetch_chain)
    t = sub.add_parser("paper", help="demo paper BUY of one ATM CE")
    t.add_argument("--symbol", default="NIFTY")
    t.add_argument("--qty", type=int, default=50)
    t.add_argument("--capital", type=float, default=100000)
    t.add_argument("--max-loss", type=float, default=settings.MAX_DAILY_LOSS)
    t.add_argument("--max-qty", type=int, default=settings.MAX_POSITION_QTY)
    t.set_defaults(fn=cmd_paper)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
