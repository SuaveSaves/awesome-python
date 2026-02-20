from __future__ import annotations

import argparse
import logging

from .bot import FomoTradingBot
from .config import BotConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FOMO auto-trading bot")
    parser.add_argument("--symbol", default=None, help="Trading symbol, e.g. BTC-USD")
    parser.add_argument("--live", action="store_true", help="Enable live trading. Default is dry-run mode")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()

    config = BotConfig.from_env()
    if args.symbol:
        config.trading_symbol = args.symbol
    if args.live:
        config.dry_run = False

    bot = FomoTradingBot.from_config(config)
    bot.run_forever()


if __name__ == "__main__":
    main()
