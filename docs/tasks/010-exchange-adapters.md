# Task 010 — Exchange adapters (Bybit, OKX)

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
- 