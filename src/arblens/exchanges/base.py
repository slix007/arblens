from abc import ABC, abstractmethod

from arblens.domain.models import OrderBook
from arblens.domain.models.exchange import Exchange


class ExchangeClient(ABC):
    venue: Exchange

    @abstractmethod
    async def fetch_order_book(self, symbol: str, depth: int) -> OrderBook:
        raise NotImplementedError
