import talib
import numpy as np

from opa.trading.indicator.base import BaseIndicator


class StochasticIndicator(BaseIndicator):
    NAME: str = "Stochastic"

    def __init__(self,
                 tunit: str,
                 fastk_period: int = 12,
                 slowk_period: int = 3,
                 slowk_matype: int = 0,
                 slowd_period: int = 3,
                 slowd_matype: int = 0) -> None:

        if fastk_period < 1:
            raise ValueError(f"Period must be positive integer: {fastk_period}")
        if slowk_period < 1:
            raise ValueError(f"Period must be positive integer: {slowk_period}")
        if slowk_matype < 0:
            raise ValueError(f"Period must be positive integer: {slowk_matype}")
        if slowd_period < 1:
            raise ValueError(f"Period must be positive integer: {slowd_period}")
        if slowd_matype < 0:
            raise ValueError(f"Period must be positive integer: {slowd_matype}")

        super().__init__(tunit)
        self._fastk_period = fastk_period
        self._slowk_period = slowk_period
        self._slowk_matype = slowk_matype
        self._slowd_period = slowd_period
        self._slowd_matype = slowd_matype

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.STOCH(highs,
                            lows,
                            closes,
                            self._fastk_period,
                            self._slowk_period,
                            self._slowk_matype,
                            self._slowd_period,
                            self._slowd_matype)

    def get_parameters(self) -> str:
        return f"{str(self._fastk_period)}#{str(self._slowk_period)}#{str(self._slowd_period)}"