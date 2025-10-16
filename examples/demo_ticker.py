"""Demo ticker class to demonstrate method calls in field registry."""

from datetime import datetime
from typing import Literal


class Ticker:
    """Mock cryptocurrency ticker with methods for price retrieval."""

    def __init__(self, symbol: str, fiat_price: float, crypto_price: float):
        self.symbol = symbol
        self.name = f"{symbol} Token"
        self._fiat_price = fiat_price
        self._crypto_price = crypto_price
        self._timestamp = datetime.now()

    def get_current_price(self, currency: Literal["fiat", "crypto"]) -> float:
        """Get current price in specified currency."""
        if currency == "fiat":
            return self._fiat_price
        elif currency == "crypto":
            return self._crypto_price
        else:
            return 0.0

    def get_price_change(self) -> float:
        """Get 24h price change percentage."""
        return 5.2

    def get_volume(self) -> int:
        """Get 24h trading volume."""
        return 1_234_567

    def get_timestamp(self) -> int:
        """Get last update timestamp."""
        return int(self._timestamp.timestamp())

    def format_display_name(self) -> str:
        """Get formatted display name."""
        return f"[{self.symbol}] {self.name}"


class Portfolio:
    """Mock portfolio class with nested method calls."""

    def __init__(self):
        self.balance_usd = 10000.0
        self.balance_btc = 0.5

    def get_balance(self, currency: str) -> float:
        """Get balance in specified currency."""
        if currency == "usd":
            return self.balance_usd
        elif currency == "btc":
            return self.balance_btc
        return 0.0

    def get_ticker(self, symbol: str) -> Ticker:
        """Get ticker for a symbol (demonstrates chained calls)."""
        return Ticker(symbol, 50000.0, 1.0)


def create_demo_context() -> dict:
    """Create demo context with object instances."""
    btc_ticker = Ticker("BTC", 67890.50, 1.0)
    eth_ticker = Ticker("ETH", 3456.78, 0.052)
    portfolio = Portfolio()

    return {
        "btc": btc_ticker,
        "eth": eth_ticker,
        "portfolio": portfolio,
        "user_name": "Alice",
        "last_update": 1729012345,
    }
