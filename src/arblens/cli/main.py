import asyncio

import typer

from arblens.analytics import calc_pair_spreads, extract_best_prices
from arblens.domain.models import OrderBook
from arblens.domain.models.exchange import Exchange
from arblens.exchanges.bybit import BybitClient
from arblens.exchanges.okx import OkxClient
from arblens.exchanges.pair import ExchangePair

app = typer.Typer(help="Arblens CLI")


@app.callback()
def callback() -> None:
    """Arblens CLI for arbitrage analysis."""
    pass


@app.command()
def report(symbol: str = "BTC/USDT", depth: int = 20) -> None:
    pair = ExchangePair(BybitClient(), OkxClient())

    async def _fetch_books() -> dict[Exchange, OrderBook | BaseException]:
        requests = {
            pair.left.venue: pair.left.fetch_order_book(symbol, depth),
            pair.right.venue: pair.right.fetch_order_book(symbol, depth),
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

        best_bid, best_ask = extract_best_prices(result)
        best_prices[venue] = (best_bid, best_ask)
        typer.echo(f"{venue}: best_bid={best_bid} best_ask={best_ask}")

    spreads = calc_pair_spreads(
        best_prices[pair.left.venue],
        best_prices[pair.right.venue],
    )

    # Sell on first (hit bid) and buy on second (lift ask)
    if spreads.spread_sell is not None:
        typer.echo(f"spreadSell (leftSell - rightBuy): {spreads.spread_sell}")

    # Buy on first (lift ask) and sell on second (hit bid)
    if spreads.spread_buy is not None:
        typer.echo(f"spreadBuy (rightSell - leftBuy): {spreads.spread_buy}")


if __name__ == "__main__":
    app()
