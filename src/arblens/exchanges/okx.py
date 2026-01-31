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

_OKX_TIMEOUT = httpx.Timeout(connect=5.0, read=10.0, write=10.0, pool=10.0)
_OKX_BASE_URL = "https://www.okx.com"


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


def parse_okx_order_book(payload: dict[str, Any], symbol: str) -> OrderBook:
    code = payload.get("code")
    if code not in (None, "0", 0):
        if code in ("50011", 50011):
            raise ExchangeRateLimitError("OKX rate limit")
        message = payload.get("msg", "")
        raise ExchangeError(f"OKX API error {code}: {message}")

    data = payload.get("data")
    if not isinstance(data, list) or not data:
        raise ExchangeParseError("OKX payload missing data array")

    book = data[0]
    if not isinstance(book, dict):
        raise ExchangeParseError("OKX payload data entry is not an object")

    raw_bids = book.get("bids", [])
    raw_asks = book.get("asks", [])
    if not isinstance(raw_bids, list) or not isinstance(raw_asks, list):
        raise ExchangeParseError("OKX payload missing bids/asks arrays")

    bids = sorted(_parse_levels(raw_bids), key=lambda level: level.price, reverse=True)
    asks = sorted(_parse_levels(raw_asks), key=lambda level: level.price)

    timestamp_value = book.get("ts")
    if timestamp_value is None:
        timestamp = datetime.now(UTC)
    else:
        try:
            timestamp_ms = int(timestamp_value)
        except (ValueError, TypeError) as exc:
            raise ExchangeParseError("OKX payload has invalid timestamp") from exc
        timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)

    return OrderBook(
        bids=bids,
        asks=asks,
        timestamp=timestamp,
        venue="okx",
        symbol=canonical_symbol(symbol),
    )


class OkxClient(ExchangeClient):
    venue = "okx"

    async def fetch_order_book(self, symbol: str, depth: int) -> OrderBook:
        exchange_sym = exchange_symbol(self.venue, symbol)
        params = {"instId": exchange_sym, "sz": str(depth)}

        async with httpx.AsyncClient(base_url=_OKX_BASE_URL, timeout=_OKX_TIMEOUT) as client:
            try:
                response = await client.get("/api/v5/market/books", params=params)
            except httpx.TimeoutException as exc:
                raise ExchangeError("OKX request timed out") from exc
            except httpx.HTTPError as exc:
                raise ExchangeError("OKX request failed") from exc

        if response.status_code != 200:
            body_snippet = response.text[:200]
            raise ExchangeHttpError(response.status_code, body_snippet)

        try:
            payload = response.json()
        except ValueError as exc:
            raise ExchangeParseError("OKX response is not valid JSON") from exc

        if not isinstance(payload, dict):
            raise ExchangeParseError("OKX JSON response is not an object")

        return parse_okx_order_book(payload, symbol)
