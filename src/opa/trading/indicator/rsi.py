import talib
import numpy as np

from opa.trading.indicator.base import BaseIndicator


class RsiIndicator(BaseIndicator):
    NAME: str = "RSI"

    def __init__(self, tunit: str,  period: int) -> None:
        if period < 1:
            raise ValueError(f"Period must be positive integer: {period}")
        super().__init__(tunit)
        self._period = period

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.RSI(np.array(closes), timeperiod=self._period)

    def get_parameters(self) -> str:
        return str(self._period)