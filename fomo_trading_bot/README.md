# FOMO AI Trading Bot (Python)

This is a configurable **auto buy/sell bot scaffold** for a FOMO trading app.

## What it does

- Pulls latest market price from the FOMO API.
- Computes a momentum signal (short SMA vs long SMA).
- Places buy/sell market orders.
- Includes risk controls:
  - max position size,
  - stop-loss,
  - take-profit,
  - cooldown between trades.
- Starts in **dry-run mode by default** (no real orders).

## API endpoints expected

- `GET /market/ticker?symbol=BTC-USD` => `{ "last_price": "64000.0" }`
- `GET /account/positions/BTC-USD` => `{ "size": "0.001", "average_entry_price": "63800" }`
- `POST /orders` with JSON:

```json
{
  "symbol": "BTC-USD",
  "side": "buy",
  "type": "market",
  "quote_size": 25
}
```

## Setup

```bash
pip install requests
```

Environment variables:

- `FOMO_API_BASE_URL` (default: `http://localhost:8000`)
- `FOMO_API_KEY` (default: `demo-key`)
- `FOMO_SYMBOL` (default: `BTC-USD`)
- `FOMO_QUOTE_SIZE` (default: `25`)
- `FOMO_SHORT_WINDOW` (default: `5`)
- `FOMO_LONG_WINDOW` (default: `20`)
- `FOMO_MAX_POSITION` (default: `0.01`)
- `FOMO_STOP_LOSS_PCT` (default: `0.02`)
- `FOMO_TAKE_PROFIT_PCT` (default: `0.03`)
- `FOMO_POLL_INTERVAL` (default: `5`)
- `FOMO_COOLDOWN_SECONDS` (default: `30`)
- `FOMO_DRY_RUN` (default: `true`)

## Run

Dry-run mode:

```bash
python -m fomo_trading_bot.main --symbol BTC-USD
```

Live mode (real orders):

```bash
python -m fomo_trading_bot.main --symbol BTC-USD --live
```

## Notes

- Start in dry-run and verify logs before enabling live mode.
- This is a template; adapt order sizing, slippage handling, and monitoring for production use.
