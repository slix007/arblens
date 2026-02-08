import asyncio

import typer

from arblens.domain.models import OrderBook
from arblens.exchanges.bybit import BybitClient
from arblens.exchanges.okx import OkxClient

ExchangeFirst = "bybit"
ExchangeSecond = "okx"

app = typer.Typer(help="Arblens CLI")

@app.callback()
def callback() -> None:
    """Arblens CLI for arbitrage analysis."""
    pass

@app.command()
def report(symbol: str = "BTC/USDT", depth: int = 20) -> None:
    async def _fetch_books() -> dict[str, OrderBook | BaseException]:
        bybit = BybitClient()
        okx = OkxClient()
        results = await asyncio.gather(
            bybit.fetch_order_book(symbol, depth),
            okx.fetch_order_book(symbol, depth),
            return_exceptions=True,
        )
        return {ExchangeFirst: results[0], ExchangeSecond: results[1]}

    books = asyncio.run(_fetch_books())

    typer.echo(f"Report for {symbol} (depth={depth})")

    best_prices: dict[str, tuple[float | None, float | None]] = {}
    for venue, result in books.items():
        if isinstance(result, BaseException):
            typer.echo(f"{venue}: error: {result}")
            best_prices[venue] = (None, None)
            continue

        best_bid = result.bids[0].price if result.bids else None
        best_ask = result.asks[0].price if result.asks else None
        best_prices[venue] = (best_bid, best_ask)
        typer.echo(f"{venue}: best_bid={best_bid} best_ask={best_ask}")

    first_bid, first_ask = best_prices.get(ExchangeFirst, (None, None))
    second_bid, second_ask = best_prices.get(ExchangeSecond, (None, None))

    # Sell on first (hit bid) and buy on second (lift ask)
    if first_bid is not None and second_ask is not None:
        spread_sell = first_bid - second_ask
        typer.echo(
            f"spreadSell (firstSell - secondBuy): {spread_sell}"
        )

    # Buy on first (lift ask) and sell on second (hit bid)
    if first_ask is not None and second_bid is not None:
        spread_buy = second_bid - first_ask
        typer.echo(
            f"spreadBuy (secondSell - firstBuy): {spread_buy}"
        )


if __name__ == "__main__":
    app()
