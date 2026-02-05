from datetime import UTC, timedelta

import pytest

from arblens.exchanges.errors import ExchangeParseError
from arblens.exchanges.okx import parse_okx_order_book


def test_okx_orderbook_parsing() -> None:
    payload = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "ts": "1700000000456",
                "bids": [["65010", "0.6", "0", "1"], ["64950", "1.1", "0", "1"]],
                "asks": [["65110", "0.2", "0", "1"], ["65220", "0.15", "0", "1"]],
            }
        ],
    }

    order_book = parse_okx_order_book(payload, "ETH/USDT")

    assert order_book.venue == "okx"
    assert order_book.symbol == "ETH/USDT"

    assert order_book.bids[0].price == 65010.0
    assert order_book.bids[1].price == 64950.0
    assert order_book.asks[0].price == 65110.0
    assert order_book.asks[1].price == 65220.0

    assert isinstance(order_book.bids[0].size, float)
    assert isinstance(order_book.asks[0].size, float)

    assert order_book.timestamp.tzinfo is not None
    assert order_book.timestamp.utcoffset() == timedelta(0)
    assert order_book.timestamp.tzinfo is UTC


def test_prices_and_sizes_are_floats_not_strings() -> None:
    """Ensure string values from JSON are converted to float."""
    payload = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "ts": "1700000000456",
                "bids": [["65010.5", "0.6", "0", "1"]],
                "asks": [["65110.5", "0.2", "0", "1"]],
            }
        ],
    }

    order_book = parse_okx_order_book(payload, "BTC/USDT")

    # Prices must be float, not str
    assert isinstance(order_book.bids[0].price, float)
    assert isinstance(order_book.asks[0].price, float)
    assert not isinstance(order_book.bids[0].price, str)
    assert not isinstance(order_book.asks[0].price, str)

    # Sizes must be float, not str
    assert isinstance(order_book.bids[0].size, float)
    assert isinstance(order_book.asks[0].size, float)
    assert not isinstance(order_book.bids[0].size, str)
    assert not isinstance(order_book.asks[0].size, str)

    # Check actual values
    assert order_book.bids[0].price == 65010.5
    assert order_book.asks[0].price == 65110.5


def test_bids_sorted_descending() -> None:
    """Bids should be sorted by price descending (best bid first)."""
    payload = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "ts": "1700000000456",
                "bids": [
                    ["64000", "1.0", "0", "1"],
                    ["65000", "1.0", "0", "1"],
                    ["64500", "1.0", "0", "1"],
                ],
                "asks": [["66000", "1.0", "0", "1"]],
            }
        ],
    }

    order_book = parse_okx_order_book(payload, "BTC/USDT")

    prices = [level.price for level in order_book.bids]
    assert prices == sorted(prices, reverse=True), "Bids must be sorted descending"
    assert prices == [65000.0, 64500.0, 64000.0]


def test_asks_sorted_ascending() -> None:
    """Asks should be sorted by price ascending (best ask first)."""
    payload = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "ts": "1700000000456",
                "bids": [["64000", "1.0", "0", "1"]],
                "asks": [
                    ["67000", "1.0", "0", "1"],
                    ["65000", "1.0", "0", "1"],
                    ["66000", "1.0", "0", "1"],
                ],
            }
        ],
    }

    order_book = parse_okx_order_book(payload, "BTC/USDT")

    prices = [level.price for level in order_book.asks]
    assert prices == sorted(prices), "Asks must be sorted ascending"
    assert prices == [65000.0, 66000.0, 67000.0]


def test_timestamp_is_tz_aware_utc() -> None:
    """Timestamp must be timezone-aware and in UTC."""
    payload = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "ts": "1700000000000",
                "bids": [["65000", "1.0", "0", "1"]],
                "asks": [["66000", "1.0", "0", "1"]],
            }
        ],
    }

    order_book = parse_okx_order_book(payload, "BTC/USDT")

    # Must be tz-aware
    assert order_book.timestamp.tzinfo is not None, "Timestamp must be tz-aware"
    # Must be UTC
    assert order_book.timestamp.utcoffset() == timedelta(0), "Timestamp must be UTC"
    assert order_book.timestamp.tzinfo is UTC


def test_raises_on_empty_bids() -> None:
    """Should raise ExchangeParseError when bids list is empty."""
    payload = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "ts": "1700000000456",
                "bids": [],
                "asks": [["65000", "1.0", "0", "1"]],
            }
        ],
    }

    with pytest.raises(ExchangeParseError):
        parse_okx_order_book(payload, "BTC/USDT")


def test_raises_on_empty_asks() -> None:
    """Should raise ExchangeParseError when asks list is empty."""
    payload = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "ts": "1700000000456",
                "bids": [["65000", "1.0", "0", "1"]],
                "asks": [],
            }
        ],
    }

    with pytest.raises(ExchangeParseError):
        parse_okx_order_book(payload, "BTC/USDT")


def test_raises_on_invalid_price() -> None:
    """Should raise ExchangeParseError on non-numeric price."""
    payload = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "ts": "1700000000456",
                "bids": [["not_a_number", "1.0", "0", "1"]],
                "asks": [["65000", "1.0", "0", "1"]],
            }
        ],
    }

    with pytest.raises(ExchangeParseError):
        parse_okx_order_book(payload, "BTC/USDT")


def test_raises_on_invalid_size() -> None:
    """Should raise ExchangeParseError on non-numeric size."""
    payload = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "ts": "1700000000456",
                "bids": [["65000", "invalid", "0", "1"]],
                "asks": [["66000", "1.0", "0", "1"]],
            }
        ],
    }

    with pytest.raises(ExchangeParseError):
        parse_okx_order_book(payload, "BTC/USDT")


def test_raises_on_empty_data() -> None:
    """Should raise ExchangeParseError when data list is empty."""
    payload = {
        "code": "0",
        "msg": "",
        "data": [],
    }

    with pytest.raises(ExchangeParseError):
        parse_okx_order_book(payload, "BTC/USDT")


def test_raises_on_missing_timestamp() -> None:
    """Should raise ExchangeParseError when timestamp is missing."""
    payload = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "bids": [["65000", "1.0", "0", "1"]],
                "asks": [["66000", "1.0", "0", "1"]],
            }
        ],
    }

    with pytest.raises(ExchangeParseError):
        parse_okx_order_book(payload, "BTC/USDT")


def test_raises_on_invalid_timestamp() -> None:
    """Should raise ExchangeParseError on non-numeric timestamp."""
    payload = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "ts": "not_a_timestamp",
                "bids": [["65000", "1.0", "0", "1"]],
                "asks": [["66000", "1.0", "0", "1"]],
            }
        ],
    }

    with pytest.raises(ExchangeParseError):
        parse_okx_order_book(payload, "BTC/USDT")


def test_raises_on_malformed_level() -> None:
    """Should raise ExchangeParseError on level with insufficient elements."""
    payload = {
        "code": "0",
        "msg": "",
        "data": [
            {
                "ts": "1700000000456",
                "bids": [["65000"]],  # Missing size
                "asks": [["66000", "1.0", "0", "1"]],
            }
        ],
    }

    with pytest.raises(ExchangeParseError):
        parse_okx_order_book(payload, "BTC/USDT")
