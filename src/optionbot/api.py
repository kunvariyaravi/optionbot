"""Dashboard API: /health, /chain, /portfolio. What Render serves."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .config import settings
from .data.nse import atm_strike, fetch_chain
from .execution.paper import PaperPortfolio

app = FastAPI(title="OptionBot", version="0.1.0")
_portfolio = PaperPortfolio()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "env": settings.ENV}


@app.get("/chain")
def chain(symbol: str = "NIFTY") -> dict:
    try:
        data = fetch_chain(symbol)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"NSE fetch failed: {e}")
    row = atm_strike(data)
    return {"symbol": symbol.upper(), "underlying": row["underlying"], "atm_strike": row["strike"],
            "ce_ltp": row["CE"].get("lastPrice"), "pe_ltp": row["PE"].get("lastPrice")}


@app.get("/portfolio")
def portfolio() -> dict:
    return _portfolio.summary()
