from dataclasses import dataclass

from arblens.exchanges.base import ExchangeClient


@dataclass(frozen=True)
class ExchangePair:
    left: ExchangeClient
    right: ExchangeClient
