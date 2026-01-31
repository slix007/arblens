# ADR 0001 — REST polling first (before WebSockets)

## Status
Accepted

## Context
We need near-real-time market data (order books/tickers) from multiple exchanges (e.g., Bybit, OKX) to evaluate arbitrage feasibility.
Time budget is limited (~8h/week) and MVP must be production-quality (typing, tests, structure) with a clear product narrative.
Non-goal: trade execution.

## Decision
Start with REST polling for order book snapshots / top-of-book data.
Introduce WebSocket streaming later as an optional upgrade once the domain model, analytics, and reliability patterns are validated.

## Rationale
- **Speed to MVP:** REST is simpler to implement, test (fixtures), and reason about.
- **Reliability & debuggability:** polling is easier to retry, rate-limit, and observe; failures are localized to requests.
- **Data quality:** snapshot-based order book avoids implementing full incremental book maintenance early (sequence numbers, missed updates, resync logic).
- **PO trade-off:** MVP value is identifying whether opportunities exist at all; sub-second freshness is not required initially.

## Consequences
### Positive
- Faster end-to-end slice: fetch → normalize → analyze → report.
- Easier strict typing + unit tests for parsing and analytics.
- Lower operational complexity (no long-lived connections).

### Negative / Risks
- Higher latency and potentially stale data vs WS.
- More API calls (rate-limit risk).
- Snapshot depth may be limited by API.

## Mitigations
- Add staleness/latency metrics in analytics (later tasks).
- Implement per-exchange rate limiting and exponential backoff.
- Keep exchange adapter interface compatible with both REST and WS backends.
- Plan a WS milestone after MVP proves useful.

## Alternatives considered
1) WebSockets first:
    - Rejected for MVP due to complexity (incremental book sync, reconnection, missed message handling).
2) Third-party aggregators:
    - Rejected to keep control, transparency, and avoid external dependency risk.