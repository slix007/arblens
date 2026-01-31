class ExchangeError(Exception):
    """Base error for exchange adapter failures."""


class ExchangeHttpError(ExchangeError):
    def __init__(self, status_code: int, body_snippet: str) -> None:
        super().__init__(f"Exchange HTTP {status_code}: {body_snippet}")
        self.status_code = status_code
        self.body_snippet = body_snippet


class ExchangeParseError(ExchangeError):
    """Raised when payloads cannot be parsed or validated."""


class ExchangeRateLimitError(ExchangeError):
    """Raised when an exchange rate-limits the request."""
