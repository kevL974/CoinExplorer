import numpy as np
import talib

from opa.trading.indicator.base import BaseIndicator


class SmaIndicator(BaseIndicator):
    NAME: str = "SMA"

    def __init__(self, tunit: str, period: int) -> None:
        super().__init__(tunit)
        if period < 1:
            raise ValueError(f"Period must be positive integer: {period}")
        self._period = period

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.SMA(closes, timeperiod=self._period)

    def get_parameters(self) -> str:
        return str(self._period)