from abc import ABC, abstractmethod
from typing import Dict

from kafka.errors import IllegalArgumentError
import talib
from opa.utils import TsQueue
from opa.core.candlestick import Candlestick
from opa.util.binance.enums import *
import numpy as np


class Indicator(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        pass


class SmaIndicator(Indicator):
    NAME: str = "SMA"

    def __init__(self, period: int) -> None:
        super().__init__()
        if period < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {period}")
        self._period = period

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.SMA(closes, timeperiod=self._period)


    def __str__(self) -> str:
        return f"{self.NAME}-{str(self._period)}"


class RsiIndicator(Indicator):
    NAME: str = "RSI"

    def __init__(self, period: int) -> None:
        if period < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {period}")
        super().__init__()
        self._period = period

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.RSI(np.array(closes), timeperiod=self._period)

    def __str__(self) -> str:
        return f"{self.NAME}-{str(self._period)}"


class StochasticIndicator(Indicator):
    NAME: str = "Stochastic"

    def __init__(self,
                 fastk_period: int = 12,
                 slowk_period: int = 3,
                 slowk_matype: int = 0,
                 slowd_period: int = 3,
                 slowd_matype: int = 0) -> None:

        if fastk_period < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {fastk_period}")
        if slowk_period < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {slowk_period}")
        if slowk_matype < 0:
            raise IllegalArgumentError(f"Period must be positive integer: {slowk_matype}")
        if slowd_period < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {slowd_period}")
        if slowd_matype < 0:
            raise IllegalArgumentError(f"Period must be positive integer: {slowd_matype}")

        super().__init__()
        self._fastk_period = fastk_period
        self._slowk_period = slowk_period
        self._slowk_matype = slowk_matype
        self._slowd_period = slowd_period
        self._slowd_matype = slowd_matype

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.STOCH(highs,
                            closes,
                            lows,
                            self._fastk_period,
                            self._slowk_period,
                            self._slowk_matype,
                            self._slowd_period,
                            self._slowd_matype)

    def __str__(self) -> str:
        return f"{self.NAME}-{str(self._fastk_period)}-{str(self._slowk_period)}-{str(self._slowd_period)}"


class MACDIndicator(Indicator):
    NAME: str = "MACD"

    def __init__(self,
                 fastperiod: int = 12,
                 slowperiod: int = 26,
                 signalperiod: int = 9) -> None:
        if fastperiod < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {fastperiod}")
        if slowperiod < 1 :
            raise IllegalArgumentError(f"Period must be positive integer: {slowperiod}")
        if signalperiod < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {signalperiod}")

        super().__init__()
        self._fastperiod: int = fastperiod
        self._slowperiod: int = slowperiod
        self._signalperiod: int = signalperiod

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.MACD(closes, self._fastperiod, self._slowperiod, self._signalperiod)

    def __str__(self) -> str:
        return f"{self.NAME}-{str(self._fastperiod)}-{str(self._slowperiod)}-{str(self._signalperiod)}"


class ParabolicSARIndicator(Indicator):
    NAME: str = "SAR"

    def __init__(self, acceleration: float, maximum: float) -> None:
        super().__init__()
        if (acceleration < 0) or (maximum < 0):
            raise ValueError()

        self._acceleration: float = acceleration
        self._maximum: float = maximum

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.SAR(highs, lows, acceleration=0.02, maximum=0.2)

    def __str__(self) -> str:
        return f"{self.NAME}-{str(self._acceleration)}-{str(self._maximum)}"


class IndicatorSet:
    __MAXSIZE: int = 200

    def __init__(self):
        self._indicators: Dict[str, Dict[str, Indicator]] = {}
        self._indicator_ts: Dict[str, np.ndarray] = {}
        self._closes: Dict[str, TsQueue] = {}
        self._highs: Dict[str, TsQueue] = {}
        self._lows: Dict[str, TsQueue] = {}
        self.__configure_queues()

    def add(self, tunit, indicator: Indicator):
        if tunit not in INTERVALS:
            raise IllegalArgumentError(f"Time unit {tunit} is not permitted")

        self.__add_price_history(tunit)
        self.__add_indicator(tunit, indicator)

    def __configure_queues(self) -> None:
        pass

    def __add_price_history(self, tunit: str) -> None:
        if tunit not in self._closes.keys():
            self._closes[tunit] = TsQueue(maxlen=IndicatorSet.__MAXSIZE)

        if tunit not in self._lows.keys():
            self._lows[tunit] = TsQueue(maxlen=IndicatorSet.__MAXSIZE)

        if tunit not in self._highs.keys():
            self._highs[tunit] = TsQueue(maxlen=IndicatorSet.__MAXSIZE)

    def __add_indicator(self, tunit: str, indicator: Indicator) -> None:
        indicator_id = self.create_id(tunit, indicator)

        if tunit not in self._indicators.keys():
            self._indicators[tunit] = {}

        if not self.indicator_exist(indicator_id):
            self._indicators[tunit][indicator_id] = indicator
            self._indicator_ts[indicator_id] = np.array([np.nan] for x in range(0, IndicatorSet.__MAXSIZE, 1))

    def __update_indicators(self, tunit: str) -> None:
        np_highs = self._highs[tunit].values()
        np_lows = self._lows[tunit].values()
        np_closes = self._closes[tunit].values()

        for id, indicator in self._indicators[tunit].items():
            self._indicator_ts[id] = indicator.value(np_highs, np_lows, np_closes)

    def get_indicator_history(self, indicator_id: str) -> np.ndarray:
        if not self.indicator_exist(indicator_id):
            raise KeyError(f"Indicator {indicator_id} does not exist")

        return self._indicator_ts[indicator_id]


    def get_indicator_value(self, indicator_id: str) -> float:
        indicator_history = self.get_indicator_history(indicator_id)

        return indicator_history[-1]

    def indicator_exist(self, indicator_id: str) -> bool:
        for tunit, indicators in self._indicators.items():
            if indicator_id in indicators.keys():
                return True

        return False

    def receive_new_candlestick(self, candlestick: Candlestick) -> None:
        tunit = candlestick.interval
        ts = candlestick.close_time
        close = candlestick.close
        low = candlestick.low
        high = candlestick.high

        self._closes[tunit].append(ts,close)
        self._lows[tunit].append(ts, low)
        self._highs[tunit].append(ts, high)

        self.__update_indicators(tunit)

    @staticmethod
    def create_id(tunit: str, indicator: Indicator) -> str:
        return f"{tunit}-{indicator.__str__()}"


