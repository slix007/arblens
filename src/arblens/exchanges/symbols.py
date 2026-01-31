_INPUT_TO_CANONICAL = {
    "BTC/USDT": "BTC/USDT",
    "BTC-USDT": "BTC/USDT",
    "BTCUSDT": "BTC/USDT",
    "ETH/USDT": "ETH/USDT",
    "ETH-USDT": "ETH/USDT",
    "ETHUSDT": "ETH/USDT",
}

_CANONICAL_TO_EXCHANGE = {
    "BTC/USDT": {"bybit": "BTCUSDT", "okx": "BTC-USDT"},
    "ETH/USDT": {"bybit": "ETHUSDT", "okx": "ETH-USDT"},
}


def canonical_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    try:
        return _INPUT_TO_CANONICAL[normalized]
    except KeyError as exc:  # pragma: no cover - exercised via exchange adapters
        raise ValueError(f"Unsupported symbol: {symbol}") from exc


def exchange_symbol(venue: str, symbol: str) -> str:
    canonical = canonical_symbol(symbol)
    try:
        return _CANONICAL_TO_EXCHANGE[canonical][venue]
    except KeyError as exc:
        raise ValueError(f"Unsupported venue or symbol: {venue} {symbol}") from exc
