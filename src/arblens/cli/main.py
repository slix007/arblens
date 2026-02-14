import asyncio
from dataclasses import dataclass
from enum import StrEnum

import typer

from arblens.domain.models import OrderBook
from arblens.exchanges.bybit import BybitClient
from arblens.exchanges.okx import OkxClient


class Exchange(StrEnum):
    BYBIT = "bybit"
    OKX = "okx"


@dataclass(frozen=True)
class VenuePair:
    left: Exchange
    right: Exchange


app = typer.Typer(help="Arblens CLI")


@app.callback()
def callback() -> None:
    """Arblens CLI for arbitrage analysis."""
    pass


@app.command()
def report(symbol: str = "BTC/USDT", depth: int = 20) -> None:
    pair = VenuePair(Exchange.BYBIT, Exchange.OKX)

    async def _fetch_books() -> dict[Exchange, OrderBook | BaseException]:
        bybit = BybitClient()
        okx = OkxClient()
        requests = {
            pair.left: bybit.fetch_order_book(symbol, depth),
            pair.right: okx.fetch_order_book(symbol, depth),
        }
        results = await asyncio.gather(*requests.values(), return_exceptions=True)
        return dict(zip(requests.keys(), results, strict=True))

    books = asyncio.run(_fetch_books())

    typer.echo(f"Report for {symbol} (depth={depth})")

    best_prices: dict[Exchange, tuple[float | None, float | None]] = {}
    for venue, result in books.items():
        if isinstance(result, BaseException):
            typer.echo(f"{venue}: error: {result}")
            best_prices[venue] = (None, None)
            continue

        best_bid = result.bids[0].price if result.bids else None
        best_ask = result.asks[0].price if result.asks else None
        best_prices[venue] = (best_bid, best_ask)
        typer.echo(f"{venue}: best_bid={best_bid} best_ask={best_ask}")

    left_bid, left_ask = best_prices.get(pair.left, (None, None))
    right_bid, right_ask = best_prices.get(pair.right, (None, None))

    # Sell on first (hit bid) and buy on second (lift ask)
    if left_bid is not None and right_ask is not None:
        spread_sell = left_bid - right_ask
        typer.echo(f"spreadSell (leftSell - rightBuy): {spread_sell}")

    # Buy on first (lift ask) and sell on second (hit bid)
    if left_ask is not None and right_bid is not None:
        spread_buy = right_bid - left_ask
        typer.echo(f"spreadBuy (rightSell - leftBuy): {spread_buy}")


if __name__ == "__main__":
    app()
