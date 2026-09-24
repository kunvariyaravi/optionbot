# OptionBot — NSE/BSE options trading bot (Phase 1 scaffold)

Paper-trade Nifty/BankNifty options with a real risk engine, NSE option-chain
ingestion, and a minimal dashboard API. Deploy free on Render (see below) or
run locally.

## Quick start (local)

```powershell
cd optionbot
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m optionbot.cli fetch-chain --symbol NIFTY
python -m optionbot.cli paper --symbol NIFTY --qty 50
uvicorn optionbot.api:app --reload
# open http://localhost:8000/health
```

## What works (Phase 1)

| Module | File |
|---|---|
| Config (env + `.env`) | `src/optionbot/config.py` |
| NSE option-chain client (public API, no key) | `src/optionbot/data/nse.py` |
| Broker interface + Kite stub | `src/optionbot/data/kite.py` |
| Risk engine (position sizing, daily loss, kill switch) | `src/optionbot/risk/` |
| Paper trading portfolio | `src/optionbot/execution/paper.py` |
| Dashboard API (`/health`, `/chain`, `/portfolio`) | `src/optionbot/api.py` |
| CLI (`fetch-chain`, `paper`) | `src/optionbot/cli.py` |
| Tests | `tests/` |

## Free cloud deploy (Render)

1. Push this repo to GitHub (`kunvariyaravi/optionbot`).
2. Go to https://dashboard.render.com → **New → Blueprint** → select the repo
   (`render.yaml` in root provisions a free web service).
3. Open the service URL → `/health` should return `{"status":"ok"}`.

Notes: free Render services sleep when idle and the filesystem is ephemeral —
paper-trading state resets on restart (Postgres comes in Phase 2). Nothing
here places real orders: `kite.py` is an interface stub until API keys are
added. See `.env.example`.

## Roadmap

- Phase 2: paper-trading core loop + dashboard P&L
- Phase 3: backtesting engine + strategy framework
- Phase 4: live broker execution + Telegram alerts
