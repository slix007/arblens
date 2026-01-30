from abc import ABC, abstractmethod
from arblens.domain.models import OrderBook


class ExchangeClient(ABC):
    venue: str

    @abstractmethod
    async def fetch_order_book(self, symbol: str, depth: int) -> OrderBook:
        raise NotImplementedError
