import numpy as np
import talib

from opa.trading.indicator.base import BaseIndicator


class BollingerBdIndicator(BaseIndicator):
    NAME: str = "BOLLINGER"

    def __init__(self,tunit: str, period: int = 20, nbdevup: int =2, nbdevdn: int =2, matype: int = 0) -> None:
        super().__init__(tunit)
        if (nbdevup < 0) or (nbdevdn < 0) or (matype not in [0,1]) or (period < 20):
            raise ValueError()

        self._nbdevup: int = nbdevup
        self._nbdevdn: int = nbdevdn
        self._matype:  int = matype
        self._period: int = period

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.BBANDS(closes, self._period, self._nbdevup, self._nbdevdn, self._matype)

    def get_parameters(self) -> str:
        return f"{self._period}#{self._nbdevup}#{self._nbdevdn}#{self._matype}"
