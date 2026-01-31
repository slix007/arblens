# Task 010 — Exchange adapters (Bybit, OKX)

## Status
Done — 2026-01-31

## Goal
Fetch order book snapshots from Bybit and OKX and normalize into OrderBook.

## Context
- Domain model: OrderBook, OrderBookLevel
- Interface: ExchangeClient
- Transport: async httpx
- Depth: configurable (top N levels)

## Requirements
- Async implementation
- Explicit timeouts
- Raise domain-level error on bad responses
- Strict typing
- No trading / no auth

## Deliverables
- bybit.py
- okx.py
- unit tests for JSON parsing

## Non-goals
- WebSocket
- Rate limiting (later task)

## Implementation notes

### Endpoints
- **Bybit**: `GET /v5/market/orderbook?category=spot&symbol=BTCUSDT&limit=50`
- **OKX**: `GET /api/v5/market/books?instId=BTC-USDT&sz=50`

### Response format
- Prices/sizes: **strings** (parse via `Decimal(str(val))`)
- Timestamps: milliseconds (Bybit: `int`, OKX: `string`)
- Bybit: `result.b/a` as `[[price, size], ...]`
- OKX: `data[0].bids/asks` as `[[price, size, _, _], ...]`

### Ordering
- Bids: sort descending by price
- Asks: sort ascending by price

### Error mapping
| Condition | Exception |
|-----------|-----------|
| `retCode != 0` / `code != "0"` | `ExchangeAPIError` |
| Timeout / connection | `ExchangeNetworkError` |
| Invalid JSON / missing fields | `ExchangeParseError` |

### Edge cases
- Empty book → empty lists
- Invalid/zero levels → skip silently
- Missing timestamp → fallback to `datetime.now(UTC)`
