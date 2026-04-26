import numpy as np
import talib

from opa.trading.indicator.base import BaseIndicator


class ParabolicSARIndicator(BaseIndicator):
    NAME: str = "SAR"

    def __init__(self, tunit: str, acceleration: float, maximum: float) -> None:
        super().__init__(tunit)
        if (acceleration < 0) or (maximum < 0):
            raise ValueError()

        self._acceleration: float = acceleration
        self._maximum: float = maximum

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.SAR(highs, lows, acceleration=self._acceleration, maximum=self._maximum)

    def get_parameters(self) -> str:
        return f"{str(self._acceleration)}#{str(self._maximum)}"
