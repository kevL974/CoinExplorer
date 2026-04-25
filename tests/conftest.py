import numpy as np
import pytest

from opa.core.candlestick import Candlestick
from opa.trading.services import Environment
from opa.trading.indicator.sma import SmaIndicator
from opa.trading.indicator.rsi import RsiIndicator
from opa.trading.indicator.macd import MACDIndicator
from opa.trading.indicator.bollinger import BollingerBdIndicator
from opa.trading.indicator.stochastic import StochasticIndicator
from opa.trading.steps.base import BaseTradingStep


def make_candlestick(
    symbol: str = "BTCUSDT",
    interval: str = "5m",
    open_price: float = 100.0,
    close_price: float = 105.0,
    high: float = 110.0,
    low: float = 95.0,
    volume: float = 1000.0,
    close_time: int = 1700000000,
) -> Candlestick:
    return Candlestick(symbol, interval, open_price, close_price, high, low, volume, close_time)


def fill_environment(env: Environment, closes: np.ndarray, interval: str = "5m") -> None:
    """Populate an environment's price history with synthetic candlesticks."""
    highs = closes * 1.02
    lows = closes * 0.98
    for i, c in enumerate(closes):
        cs = Candlestick(
            "BTCUSDT", interval,
            float(c), float(c),
            float(highs[i]), float(lows[i]),
            1000.0,
            1700000000 + i * 300,
        )
        env.put(cs)


@pytest.fixture
def price_arrays() -> dict:
    """200 synthetic OHLCV arrays — bull trend (close goes from 100 to 200)."""
    n = 200
    closes = np.linspace(100.0, 200.0, n)
    return {"closes": closes, "highs": closes * 1.02, "lows": closes * 0.98}


@pytest.fixture
def filled_environment() -> Environment:
    """Real Environment pre-filled with 200 bull-trend 5m candles + standard indicators."""
    env = Environment()
    for ind in [
        SmaIndicator("5m", 20),
        SmaIndicator("5m", 50),
        RsiIndicator("5m", 14),
        MACDIndicator("5m", 12, 26, 9),
        BollingerBdIndicator("5m", 20, 2, 2, 0),
        StochasticIndicator("5m", 5, 3, 0, 3, 0),
    ]:
        env.indicators_manager.add("5m", ind)
    fill_environment(env, np.linspace(100.0, 200.0, 200), "5m")
    return env


class TerminalStep(BaseTradingStep):
    """Sentinel step for tests: marks a successful transition without advancing further."""
    def check_condition(self) -> None:
        pass
    def on_success(self) -> None:
        pass
    def on_fail(self) -> None:
        pass
    def on_wait(self) -> None:
        pass
