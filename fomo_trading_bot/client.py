from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass(slots=True)
class Position:
    size: float = 0.0
    average_entry_price: float = 0.0


class FomoApiClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def get_last_price(self, symbol: str) -> float:
        response = self.session.get(
            f"{self.base_url}/market/ticker", params={"symbol": symbol}, timeout=self.timeout
        )
        response.raise_for_status()
        payload = response.json()
        return float(payload["last_price"])

    def get_position(self, symbol: str) -> Position:
        response = self.session.get(
            f"{self.base_url}/account/positions/{symbol}", timeout=self.timeout
        )
        if response.status_code == 404:
            return Position()
        response.raise_for_status()
        payload = response.json()
        return Position(
            size=float(payload.get("size", 0.0)),
            average_entry_price=float(payload.get("average_entry_price", 0.0)),
        )

    def place_market_order(self, symbol: str, side: str, quote_size: float) -> dict:
        response = self.session.post(
            f"{self.base_url}/orders",
            json={
                "symbol": symbol,
                "side": side,
                "type": "market",
                "quote_size": quote_size,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
