# Task 020 — Spread, Slippage, and Net Arbitrage Evaluation

## Status

Planned — Week 2

## Goal

Move from raw top-of-book spread to realistic arbitrage feasibility evaluation:

- Account for order book depth
- Compute effective execution price for a given size
- Apply taker fees
- Calculate gross spread and net spread
- Estimate capacity

This task transforms Arblens from "price comparison tool" into a decision-support system.

---

## Scope

### In Scope

- Slippage model (walk the book)
- Fee model (taker-only)
- Net spread calculation
- Refactor spread logic out of CLI into `analytics/`
- Unit tests for analytics functions

### Out of Scope

- WebSocket
- Funding rates
- Transfer delays
- Partial fills strategy
- Market impact modeling beyond visible order book
- Persistence (DB/storage)

---

## Product / Tech Contract

### Terminology

- `firstSell` = best bid on first exchange
- `secondBuy` = best ask on second exchange
- `spreadSell = firstSell - secondBuy`

- `firstBuy` = best ask on first exchange
- `secondSell` = best bid on second exchange
- `spreadBuy = secondSell - firstBuy`

---

### Slippage Model

Given:

- Order book levels (price, size)
- Target execution size (base currency)

The system must:

- Walk the order book from top level down
- Accumulate size until requested size is satisfied
- Compute weighted average execution price
- If insufficient liquidity:
    - return partial fill information

---

### Fee Model

Assumptions:

- Taker fees only
- Fees applied multiplicatively

For a fee `f`:

- Buy: `price * (1 + f)`
- Sell: `price * (1 - f)`

No maker fees.
No dynamic tier logic (yet).

---

### Net Spread Definition

For a given size:

1. Compute effective execution prices on both exchanges
2. Apply fees
3. Compute:
   gross_spread = first_execution_price - second_execution_price
   net_spread = gross_spread - fees_impact

Alternatively:
Net spread can be computed directly using fee-adjusted effective prices.

---

### Capacity

Capacity is defined as:

> Maximum size for which net spread remains positive.

For Week 2:

- Capacity may be approximated using available visible liquidity
- No advanced optimization required

---

## Deliverables

### New Modules

analytics/
spread.py
slippage.py
fees.py

---

### slippage.py

Implement:

```python
def effective_price(
        levels: Sequence[OrderBookLevel],
        size: float
) -> float:
    ...
```

Behavior:
• Weighted average execution price
• Deterministic
• Pure function

### fees.py

```python
@dataclass
class FeeSchedule:
    taker: float
```

```python
def apply_fee(price: float, fee: float, side: Literal["buy", "sell"]) -> float
```

### spread.py

```python
@dataclass
class SpreadResult:
    gross_spread: float
    net_spread: float
    capacity: float
```

```python
def compute_net_spread(
        first_book: OrderBook,
        second_book: OrderBook,
        size: float,
        first_fee: float,
        second_fee: float,
) -> SpreadResult:
    ...
```

## CLI Changes

Update report command:

Add argument:
` --size FLOAT`
CLI must display:
• gross_spread
• net_spread
• capacity

CLI must not contain business logic — only orchestration.

## Testing Requirements

Unit tests must cover:
• Weighted average price calculation
• Insufficient liquidity handling
• Fee application correctness
• Net spread decreases after fees
• Deterministic behavior

No network calls in analytics tests.

## Definition of Done

• Spread logic fully extracted from CLI
• All analytics functions are pure and testable
• make check passes
• CLI displays gross and net spread for a given size
• Contract documented and consistent with implementation