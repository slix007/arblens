from datetime import UTC, timedelta

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
