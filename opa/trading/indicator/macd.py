import numpy as np
import talib

from opa.trading.indicator.base import BaseIndicator


class MACDIndicator(BaseIndicator):
    NAME: str = "MACD"

    def __init__(self,
                 tunit: str,
                 fastperiod: int = 12,
                 slowperiod: int = 26,
                 signalperiod: int = 9) -> None:
        if fastperiod < 1:
            raise ValueError(f"Period must be positive integer: {fastperiod}")
        if slowperiod < 1 :
            raise ValueError(f"Period must be positive integer: {slowperiod}")
        if signalperiod < 1:
            raise ValueError(f"Period must be positive integer: {signalperiod}")

        super().__init__(tunit)
        self._fastperiod: int = fastperiod
        self._slowperiod: int = slowperiod
        self._signalperiod: int = signalperiod

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.MACD(closes, self._fastperiod, self._slowperiod, self._signalperiod)

    def get_parameters(self) -> str:
        return f"{str(self._fastperiod)}#{str(self._slowperiod)}#{str(self._signalperiod)}"
