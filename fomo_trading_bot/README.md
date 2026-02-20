# FOMO AI Trading Bot (iPhone-ready)

This bot auto buys/sells using your FOMO API, and includes an **iPhone control server** so you can run it from iOS Shortcuts.

## Features

- Auto trading loop (momentum SMA strategy)
- Risk controls (max position, stop-loss, take-profit, cooldown)
- Dry-run by default
- iPhone endpoints for:
  - start bot
  - stop bot
  - run one cycle
  - force buy/sell
  - status check

## Expected FOMO API

- `GET /market/ticker?symbol=BTC-USD` => `{ "last_price": "64000.0" }`
- `GET /account/positions/BTC-USD` => `{ "size": "0.001", "average_entry_price": "63800" }`
- `POST /orders`

## Install

```bash
pip install -r requirements.txt
```

## Environment variables

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
- `FOMO_IPHONE_TOKEN` (**required** for iPhone control API auth)

## Run bot directly

```bash
python -m fomo_trading_bot.main --symbol BTC-USD
```

## Run iPhone control server

```bash
export FOMO_IPHONE_TOKEN="change-me"
python -m fomo_trading_bot.iphone_server --host 0.0.0.0 --port 8787
```

## iPhone endpoints (for Shortcuts)

All POST endpoints need header: `X-Bot-Token: <FOMO_IPHONE_TOKEN>`

- `GET /health`
- `GET /status`
- `POST /start`
- `POST /stop`
- `POST /run-once`
- `POST /trade` with JSON `{ "action": "buy" }` or `{ "action": "sell" }`

## iOS Shortcut example

1. Open **Shortcuts** on iPhone.
2. Add action: **Get Contents of URL**.
3. URL: `https://<your-server>/run-once`
4. Method: `POST`
5. Add header: `X-Bot-Token` = your token.
6. (Optional) Add **Show Result** to view JSON output.

## Safety

- Keep `FOMO_DRY_RUN=true` while testing.
- Never expose the server without HTTPS and a strong token.
- Consider IP allowlists / reverse proxy auth for production.
