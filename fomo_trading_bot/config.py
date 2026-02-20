from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class BotConfig:
    api_base_url: str
    api_key: str
    trading_symbol: str = "BTC-USD"
    quote_size: float = 25.0
    short_window: int = 5
    long_window: int = 20
    max_position_size: float = 0.01
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.03
    poll_interval_seconds: float = 5.0
    cooldown_seconds: float = 30.0
    dry_run: bool = True

    @classmethod
    def from_env(cls) -> "BotConfig":
        return cls(
            api_base_url=os.getenv("FOMO_API_BASE_URL", "http://localhost:8000"),
            api_key=os.getenv("FOMO_API_KEY", "demo-key"),
            trading_symbol=os.getenv("FOMO_SYMBOL", "BTC-USD"),
            quote_size=float(os.getenv("FOMO_QUOTE_SIZE", "25")),
            short_window=int(os.getenv("FOMO_SHORT_WINDOW", "5")),
            long_window=int(os.getenv("FOMO_LONG_WINDOW", "20")),
            max_position_size=float(os.getenv("FOMO_MAX_POSITION", "0.01")),
            stop_loss_pct=float(os.getenv("FOMO_STOP_LOSS_PCT", "0.02")),
            take_profit_pct=float(os.getenv("FOMO_TAKE_PROFIT_PCT", "0.03")),
            poll_interval_seconds=float(os.getenv("FOMO_POLL_INTERVAL", "5")),
            cooldown_seconds=float(os.getenv("FOMO_COOLDOWN_SECONDS", "30")),
            dry_run=os.getenv("FOMO_DRY_RUN", "true").lower() in {"1", "true", "yes"},
        )
