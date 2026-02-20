from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum


class Signal(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass(slots=True)
class MomentumStrategy:
    short_window: int
    long_window: int

    def __post_init__(self) -> None:
        if self.short_window >= self.long_window:
            msg = "short_window must be smaller than long_window"
            raise ValueError(msg)
        self.prices: deque[float] = deque(maxlen=self.long_window)

    def update(self, price: float) -> Signal:
        self.prices.append(price)
        if len(self.prices) < self.long_window:
            return Signal.HOLD

        short_prices = list(self.prices)[-self.short_window :]
        short_avg = sum(short_prices) / self.short_window
        long_avg = sum(self.prices) / self.long_window

        if short_avg > long_avg:
            return Signal.BUY
        if short_avg < long_avg:
            return Signal.SELL
        return Signal.HOLD
