from __future__ import annotations

import argparse
import json
import logging
import os
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .bot import FomoTradingBot
from .config import BotConfig

logger = logging.getLogger(__name__)


class BotService:
    def __init__(self, bot: FomoTradingBot) -> None:
        self.bot = bot
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self.bot.run_forever, kwargs={"stop_event": self._stop_event}, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self.is_running:
            return
        self._stop_event.set()
        assert self._thread is not None
        self._thread.join(timeout=2)

    def force_trade(self, action: str) -> None:
        if action not in {"buy", "sell"}:
            msg = "action must be buy or sell"
            raise ValueError(msg)
        self.bot._execute(action)


class Handler(BaseHTTPRequestHandler):
    service: BotService
    token: str

    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> bool:
        expected = self.token
        provided = self.headers.get("X-Bot-Token", "")
        return bool(expected) and expected == provided

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length) if length else b"{}"
        return json.loads(data or b"{}")

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json(HTTPStatus.OK, {"status": "ok"})
            return

        if self.path == "/status":
            self._json(
                HTTPStatus.OK,
                {
                    "running": self.service.is_running,
                    "symbol": self.service.bot.config.trading_symbol,
                    "dry_run": self.service.bot.config.dry_run,
                },
            )
            return

        self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if not self._authorized():
            self._json(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            return

        if self.path == "/start":
            self.service.start()
            self._json(HTTPStatus.OK, {"status": "started"})
            return

        if self.path == "/stop":
            self.service.stop()
            self._json(HTTPStatus.OK, {"status": "stopped"})
            return

        if self.path == "/run-once":
            try:
                result = self.service.bot.run_once()
            except Exception as exc:  # noqa: BLE001
                self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return
            self._json(HTTPStatus.OK, result)
            return

        if self.path == "/trade":
            payload = self._read_json()
            action = str(payload.get("action", "")).lower()
            try:
                self.service.force_trade(action)
            except ValueError as exc:
                self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return
            self._json(HTTPStatus.OK, {"status": "ok", "action": action})
            return

        self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="iPhone-control server for FOMO bot")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8787)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()

    config = BotConfig.from_env()
    service = BotService(FomoTradingBot.from_config(config))

    Handler.service = service
    Handler.token = os.getenv("FOMO_IPHONE_TOKEN", "")

    if not Handler.token:
        msg = "FOMO_IPHONE_TOKEN is required"
        raise RuntimeError(msg)

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    logger.info("iPhone server listening on %s:%s", args.host, args.port)
    server.serve_forever()


if __name__ == "__main__":
    main()
