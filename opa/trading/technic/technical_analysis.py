from abc import ABC, abstractmethod
from typing import Tuple, Dict, List

from kafka.errors import IllegalArgumentError
from talib import stream
import talib
from opa.utils import TsQueue
from opa.core.candlestick import Candlestick
from opa.util.observer import Observer, Subject, EventType
from opa.util.binance.enums import *
import numpy as np


class Indicator(Observer):

    def __init__(self):
        super().__init__()

    def update(self) -> None:
        pass

    @abstractmethod
    def value(self, highs: TsQueue, lows: TsQueue, closes: TsQueue) -> TsQueue:
        pass


class SmaIndicator(Indicator):
    NAME: str = "SMA"

    def __init__(self, period: int) -> None:
        super().__init__()
        if period < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {period}")
        self._period = period

    def value(self, highs: TsQueue, lows: TsQueue, closes: TsQueue) -> TsQueue:

        sma = talib.SMA(closes.values(), timeperiod=self._period)
        ts = closes.timestamps()
        tsq_sma = TsQueue(maxlen=self._period)

        for ts_i, sma_i in zip(ts[-self._period:], sma[-self._period:]):
            tsq_sma.append(ts_i, sma_i)

        return tsq_sma

    def __str__(self) -> str:
        return f"{self.NAME}-{str(self._period)}"


class RsiIndicator(Indicator):
    NAME: str = "RSI"

    def __init__(self, period: int) -> None:
        if period < 1:
            raise ValueError()
        super().__init__()
        self._period = period
        self._window = TsQueue(maxlen=self._period + 1)

    def update(self, candlestick: Candlestick) -> None:
        self._window.append(ts=candlestick.close_time, value=candlestick.close)

    def value(self) -> float:
        close_time, close_price = self._window.tolist()
        return stream.RSI(np.array(close_price), timeperiod=self._period)

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
        if (fastk_period < 1) or (slowk_period < 1) or (slowk_matype < 0) or (slowd_period < 1) or (slowd_matype < 0):
            raise ValueError()

        super().__init__()
        self._fastk_period = fastk_period
        self._slowk_period = slowk_period
        self._slowk_matype = slowk_matype
        self._slowd_period = slowd_period
        self._slowd_matype = slowd_matype
        self._window_high: TsQueue = TsQueue(maxlen=self._fastk_period + 5)
        self._window_close: TsQueue = TsQueue(maxlen=self._fastk_period + 5)
        self._window_low: TsQueue = TsQueue(maxlen=self._fastk_period + 5)

    def update(self, candlestick: Candlestick) -> None:
        self._window_high.append(ts=candlestick.close_time, value=candlestick.high)
        self._window_close.append(ts=candlestick.close_time, value=candlestick.close)
        self._window_low.append(ts=candlestick.close_time, value=candlestick.low)

    def value(self) -> float:
        high = np.array(self._window_high.tolist()[1])
        close = np.array(self._window_close.tolist()[1])
        low = np.array(self._window_low.tolist()[1])

        return stream.STOCH(high,
                            close,
                            low,
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
        if (fastperiod < 1) or (slowperiod < 1) or (signalperiod < 1):
            raise ValueError()
        super().__init__()
        self._fastperiod: int = fastperiod
        self._slowperiod: int = slowperiod
        self._signalperiod: int = signalperiod
        self._window: TsQueue = TsQueue(maxlen=self._slowperiod + self._fastperiod)

    def update(self, candlestick: Candlestick) -> None:
        self._window.append(ts=candlestick.close_time, value=candlestick.close)

    def value(self) -> float:
        close_time, close = np.array(self._window.tolist())
        return stream.MACD(close, self._fastperiod, self._slowperiod, self._signalperiod)

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
        self._window_high: TsQueue = TsQueue()
        self._window_low: TsQueue = TsQueue()

    def update(self, candlestick: Candlestick) -> None:
        self._window_high.append(ts=candlestick.close_time, value=candlestick.high)
        self._window_low.append(ts=candlestick.close_time, value=candlestick.low)

    def value(self) -> float:
        high = np.array(self._window_high.tolist()[1])
        low = np.array(self._window_low.tolist()[1])
        return stream.SAR(high, low, acceleration=0.02, maximum=0.2)

    def __str__(self) -> str:
        return f"{self.NAME}-{str(self._acceleration)}-{str(self._maximum)}"


class IndicatorSet:
    __MAXSIZE: int = 200

    def __init__(self):
        self._indicators: Dict[str, Indicator] = {}
        self._indicator_ts: Dict[str, TsQueue] = {}
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

        if not self.indicator_exist(indicator_id):
            self._indicators[indicator_id] = indicator
            self._indicator_ts[indicator_id] = TsQueue()

    def get_indicator_history(self, indicator_id: str) -> TsQueue:
        if not self.indicator_exist(indicator_id):
            raise KeyError(f"Indicator {indicator_id} does not exist")

        return self._indicator_ts[indicator_id]


    def get_indicator_value(self, indicator_id: str) -> Tuple[int, float]:
        if not self.indicator_exist(indicator_id):
            raise KeyError(f"Indicator {indicator_id} does not exist")

        indicator_history = self.get_indicator_history(indicator_id)

        return indicator_history.last_entry()

    def indicator_exist(self, indicator_id: str) -> bool:
        return indicator_id in self._indicators.keys()

    def receive_new_candlestick(self, candlestick: Candlestick) -> None:
        tunit = candlestick.interval
        ts = candlestick.close_time
        close = candlestick.close
        low = candlestick.low
        high = candlestick.high

        self._closes[tunit].append(ts,close)
        self._lows[tunit].append(ts, low)
        self._highs[tunit].append(ts, high)

        for id, indicator in self._indicators.items():
            self._indicator_ts[id] = self._indicators[id].value(self._highs, self._lows, self._closes)



    @staticmethod
    def create_id(tunit: str, indicator: Indicator) -> str:
        return f"{tunit}-{indicator.__str__()}"


