from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from .client import FomoApiClient, Position
from .config import BotConfig
from .strategy import MomentumStrategy, Signal

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class FomoTradingBot:
    config: BotConfig
    client: FomoApiClient
    strategy: MomentumStrategy

    @classmethod
    def from_config(cls, config: BotConfig) -> "FomoTradingBot":
        return cls(
            config=config,
            client=FomoApiClient(config.api_base_url, config.api_key),
            strategy=MomentumStrategy(config.short_window, config.long_window),
        )

    def _risk_allows_buy(self, position: Position) -> bool:
        return position.size < self.config.max_position_size

    def _risk_requires_sell(self, position: Position, last_price: float) -> bool:
        if position.size <= 0 or position.average_entry_price <= 0:
            return False
        change = (last_price - position.average_entry_price) / position.average_entry_price
        return change <= -self.config.stop_loss_pct or change >= self.config.take_profit_pct

    def _execute(self, side: str) -> None:
        if self.config.dry_run:
            logger.info("[dry-run] %s %s with quote size %.2f", side.upper(), self.config.trading_symbol, self.config.quote_size)
            return

        order = self.client.place_market_order(
            symbol=self.config.trading_symbol,
            side=side,
            quote_size=self.config.quote_size,
        )
        logger.info("Order placed: %s", order)

    def run_forever(self) -> None:
        logger.info("Starting bot for %s (dry_run=%s)", self.config.trading_symbol, self.config.dry_run)
        last_trade_ts = 0.0

        while True:
            now = time.time()
            if now - last_trade_ts < self.config.cooldown_seconds:
                time.sleep(self.config.poll_interval_seconds)
                continue

            try:
                price = self.client.get_last_price(self.config.trading_symbol)
                position = self.client.get_position(self.config.trading_symbol)
                signal = self.strategy.update(price)

                logger.info(
                    "price=%.2f signal=%s position(size=%.6f, entry=%.2f)",
                    price,
                    signal.value,
                    position.size,
                    position.average_entry_price,
                )

                if self._risk_requires_sell(position, price):
                    self._execute("sell")
                    last_trade_ts = now
                elif signal is Signal.BUY and self._risk_allows_buy(position):
                    self._execute("buy")
                    last_trade_ts = now
                elif signal is Signal.SELL and position.size > 0:
                    self._execute("sell")
                    last_trade_ts = now

            except Exception:
                logger.exception("Bot iteration failed")

            time.sleep(self.config.poll_interval_seconds)
