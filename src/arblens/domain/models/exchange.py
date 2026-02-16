from dataclasses import dataclass
from enum import StrEnum


class Exchange(StrEnum):
    BYBIT = "bybit"
    OKX = "okx"


@dataclass(frozen=True)
class PairSpread:
    spread_sell: float | None
    spread_buy: float | None
