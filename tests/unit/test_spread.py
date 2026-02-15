from datetime import UTC, datetime

from arblens.analytics import PairSpread, calc_pair_spreads, extract_best_prices
from arblens.domain.models import OrderBook, OrderBookLevel


def _build_order_book(
    bids: list[tuple[float, float]], asks: list[tuple[float, float]]
) -> OrderBook:
    return OrderBook(
        bids=[OrderBookLevel(price=price, size=size) for price, size in bids],
        asks=[OrderBookLevel(price=price, size=size) for price, size in asks],
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        venue="test",
        symbol="BTC/USDT",
    )


def test_extract_best_prices_returns_top_of_book() -> None:
    order_book = _build_order_book(
        bids=[(65000.0, 1.2), (64900.0, 0.7)],
        asks=[(65100.0, 0.4), (65200.0, 0.6)],
    )

    best_bid, best_ask = extract_best_prices(order_book)

    assert best_bid == 65000.0
    assert best_ask == 65100.0


def test_extract_best_prices_handles_empty_sides() -> None:
    no_bids = _build_order_book(bids=[], asks=[(65100.0, 0.4)])
    no_asks = _build_order_book(bids=[(65000.0, 1.2)], asks=[])

    assert extract_best_prices(no_bids) == (None, 65100.0)
    assert extract_best_prices(no_asks) == (65000.0, None)


def test_calc_pair_spreads_returns_both_directions() -> None:
    spreads = calc_pair_spreads(
        left_prices=(65010.0, 65020.0),
        right_prices=(65030.0, 65040.0),
    )

    assert spreads == PairSpread(spread_sell=-30.0, spread_buy=10.0)


def test_calc_pair_spreads_returns_none_for_missing_prices() -> None:
    assert calc_pair_spreads((None, 65020.0), (65030.0, 65040.0)) == PairSpread(
        spread_sell=None,
        spread_buy=10.0,
    )
    assert calc_pair_spreads((65010.0, None), (65030.0, None)) == PairSpread(
        spread_sell=None,
        spread_buy=None,
    )
