from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from arblens.domain.models import OrderBook, OrderBookLevel
from arblens.exchanges.base import ExchangeClient
from arblens.exchanges.errors import (
    ExchangeError,
    ExchangeHttpError,
    ExchangeParseError,
    ExchangeRateLimitError,
)
from arblens.exchanges.symbols import canonical_symbol, exchange_symbol

_BYBIT_TIMEOUT = httpx.Timeout(connect=5.0, read=10.0, write=10.0, pool=10.0)
_BYBIT_BASE_URL = "https://api.bybit.com"


def _parse_levels(raw_levels: Iterable[Iterable[Any]]) -> list[OrderBookLevel]:
    levels: list[OrderBookLevel] = []
    for raw_level in raw_levels:
        items = list(raw_level)
        if len(items) < 2:
            continue
        try:
            price = float(Decimal(str(items[0])))
            size = float(Decimal(str(items[1])))
        except (InvalidOperation, ValueError, TypeError):
            continue
        # Skip invalid/zero levels to keep snapshots usable.
        if price <= 0 or size <= 0:
            continue
        levels.append(OrderBookLevel(price=price, size=size))
    return levels


def parse_bybit_order_book(payload: dict[str, Any], symbol: str) -> OrderBook:
    ret_code = payload.get("retCode")
    if ret_code not in (0, "0", None):
        if ret_code in (10006, "10006"):
            raise ExchangeRateLimitError("Bybit rate limit")
        ret_msg = payload.get("retMsg", "")
        raise ExchangeError(f"Bybit API error {ret_code}: {ret_msg}")

    try:
        result = payload["result"]
    except KeyError as exc:
        raise ExchangeParseError("Bybit payload missing result") from exc

    if not isinstance(result, dict):
        raise ExchangeParseError("Bybit payload result is not an object")

    raw_bids = result.get("b", [])
    raw_asks = result.get("a", [])
    if not isinstance(raw_bids, list) or not isinstance(raw_asks, list):
        raise ExchangeParseError("Bybit payload missing bids/asks arrays")

    bids = sorted(_parse_levels(raw_bids), key=lambda level: level.price, reverse=True)
    asks = sorted(_parse_levels(raw_asks), key=lambda level: level.price)

    timestamp_value = result.get("ts")
    if timestamp_value is None:
        timestamp = datetime.now(UTC)
    else:
        try:
            timestamp_ms = int(timestamp_value)
        except (ValueError, TypeError) as exc:
            raise ExchangeParseError("Bybit payload has invalid timestamp") from exc
        timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)

    return OrderBook(
        bids=bids,
        asks=asks,
        timestamp=timestamp,
        venue="bybit",
        symbol=canonical_symbol(symbol),
    )


class BybitClient(ExchangeClient):
    venue = "bybit"

    async def fetch_order_book(self, symbol: str, depth: int) -> OrderBook:
        exchange_sym = exchange_symbol(self.venue, symbol)
        params = {"category": "spot", "symbol": exchange_sym, "limit": str(depth)}

        async with httpx.AsyncClient(base_url=_BYBIT_BASE_URL, timeout=_BYBIT_TIMEOUT) as client:
            try:
                response = await client.get("/v5/market/orderbook", params=params)
            except httpx.TimeoutException as exc:
                raise ExchangeError("Bybit request timed out") from exc
            except httpx.HTTPError as exc:
                raise ExchangeError("Bybit request failed") from exc

        if response.status_code != 200:
            body_snippet = response.text[:200]
            raise ExchangeHttpError(response.status_code, body_snippet)

        try:
            payload = response.json()
        except ValueError as exc:
            raise ExchangeParseError("Bybit response is not valid JSON") from exc

        if not isinstance(payload, dict):
            raise ExchangeParseError("Bybit JSON response is not an object")

        return parse_bybit_order_book(payload, symbol)
