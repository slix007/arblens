import typer

app = typer.Typer()


@app.command()
def report(symbol: str = "BTC/USDT") -> None:
    typer.echo(f"Report for {symbol} (not implemented yet)")


if __name__ == "__main__":
    app()
