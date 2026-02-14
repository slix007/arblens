from arblens.domain.models import OrderBook
from arblens.domain.models.exchange import PairSpread


def extract_best_prices(order_book: OrderBook) -> tuple[float | None, float | None]:
    """Extract best bid and ask prices from order books."""
    best_bid = order_book.bids[0].price if order_book.bids else None
    best_ask = order_book.asks[0].price if order_book.asks else None
    return best_bid, best_ask

def calc_pair_spreads(
    left_prices: tuple[float | None, float | None],
    right_prices: tuple[float | None, float | None],
) -> PairSpread:
    """Calculate spreads for both directions of the pair."""
    left_bid, left_ask = left_prices
    right_bid, right_ask = right_prices

    spread_sell = (left_bid - right_ask) if left_bid is not None and right_ask is not None else None
    spread_buy = (right_bid - left_ask) if left_ask is not None and right_bid is not None else None

    return PairSpread(spread_sell, spread_buy)