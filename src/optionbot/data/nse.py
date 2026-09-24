"""NSE public option-chain client. No API key needed.

NSE blocks bare requests, so we keep a session with browser headers and warm
up cookies on the homepage first. Fails loudly (no silent empty chains).
"""
from __future__ import annotations

import requests

from ..logging_setup import log

BASE = "https://www.nseindia.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
}

# Valid `symbol` values for the indices endpoint: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, NIFTYNXT50
INDEX_SYMBOLS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "NIFTYNXT50"}


def fetch_chain(symbol: str = "NIFTY", timeout: int = 15) -> dict:
    symbol = symbol.upper()
    if symbol not in INDEX_SYMBOLS:
        raise ValueError(f"unknown index symbol {symbol!r} (one of {sorted(INDEX_SYMBOLS)})")
    s = requests.Session()
    s.headers.update(HEADERS)
    s.get(BASE, timeout=timeout)  # warm cookies; NSE rejects cold API hits
    url = f"{BASE}/api/option-chain-indices?symbol={symbol}"
    r = s.get(url, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    records = data.get("records", {})
    log.info("fetched %s chain: expiry=%s underlying=%s strikes=%d",
             symbol, records.get("expiryDates", [None])[0],
             records.get("underlyingValue"), len(data.get("filtered", {}).get("data", [])))
    return data


def atm_strike(data: dict) -> dict:
    """Return the at-the-money strike row (nearest CE+PE pair to underlying)."""
    underlying = data["records"]["underlyingValue"]
    rows = data["filtered"]["data"]
    best = min(rows, key=lambda row: abs(row["strikePrice"] - underlying))
    return {"underlying": underlying, "strike": best["strikePrice"],
            "CE": best.get("CE", {}), "PE": best.get("PE", {})}
