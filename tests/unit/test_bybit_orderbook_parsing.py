from datetime import UTC, timedelta

from arblens.exchanges.bybit import parse_bybit_order_book


def test_bybit_orderbook_parsing() -> None:
    payload = {
        "retCode": 0,
        "retMsg": "OK",
        "result": {
            "s": "BTCUSDT",
            "b": [["65000", "0.5"], ["64900", "1.25"], ["0", "2"], ["bad", "1"]],
            "a": [["65200", "0.1"], ["65100", "0.4"], ["65300", "0"], ["oops", "3"]],
            "ts": 1700000000123,
        },
    }

    order_book = parse_bybit_order_book(payload, "BTC/USDT")

    assert order_book.venue == "bybit"
    assert order_book.symbol == "BTC/USDT"

    assert order_book.bids[0].price == 65000.0
    assert order_book.bids[1].price == 64900.0
    assert order_book.asks[0].price == 65100.0
    assert order_book.asks[1].price == 65200.0

    assert isinstance(order_book.bids[0].size, float)
    assert isinstance(order_book.asks[0].size, float)

    assert order_book.timestamp.tzinfo is not None
    assert order_book.timestamp.utcoffset() == timedelta(0)
    assert order_book.timestamp.tzinfo is UTC
