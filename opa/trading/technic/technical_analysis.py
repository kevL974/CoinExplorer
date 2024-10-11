from abc import ABC, abstractmethod
from typing import Tuple, Dict, List
from talib import stream
from opa.utils import TsQueue
from opa.core.candlestick import Candlestick
from opa.util.observer import Observer, Subject, EventType
import numpy as np


class Indicator(Observer):

    def __init__(self, tunit: str) -> None:
        self.tunit: str = tunit

    def update(self, subject: Subject) -> None:
        pass

    @abstractmethod
    def value(self) -> float:
        pass


class SmaIndicator(Indicator):
    NAME: str = "SMA"

    def __init__(self, tunit: str, period: int) -> None:
        if period < 1:
            raise ValueError()

        super().__init__(tunit)
        self._period = period
        self._window = TsQueue(maxlen=self._period)

    def update(self, candlestick: Candlestick) -> None:
        self._window.append(ts=candlestick.close_time, value=candlestick.close)

    def value(self) -> float:
        close_time, close_price = self._window.tolist()
        return stream.SMA(np.array(close_price), timeperiod=self._period)

    def __str__(self) -> str:
        return f"{self.NAME}-{str(self._period)}-{self.tunit}"


class RsiIndicator(Indicator):
    NAME: str = "RSI"

    def __init__(self, tunit: str, period: int) -> None:
        if period < 1:
            raise ValueError()
        super().__init__(tunit)
        self._period = period
        self._window = TsQueue(maxlen=self._period + 1)

    def update(self, candlestick: Candlestick) -> None:
        self._window.append(ts=candlestick.close_time, value=candlestick.close)

    def value(self) -> float:
        close_time, close_price = self._window.tolist()
        return stream.RSI(np.array(close_price), timeperiod=self._period)

    def __str__(self) -> str:
        return f"{self.NAME}-{str(self._period)}-{self.tunit}"


class StochasticIndicator(Indicator):
    NAME: str = "Stochastic"

    def __init__(self,
                 tunit: str,
                 fastk_period: int = 12,
                 slowk_period: int = 3,
                 slowk_matype: int = 0,
                 slowd_period: int = 3,
                 slowd_matype: int = 0) -> None:
        if (fastk_period < 1) or (slowk_period < 1) or (slowk_matype < 0) or (slowd_period < 1) or (slowd_matype < 0):
            raise ValueError()

        super().__init__(tunit)
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
        return f"{self.NAME}-{str(self._fastk_period)}-{str(self._slowk_period)}-{str(self._slowd_period)}-{self.tunit}"


class MACDIndicator(Indicator):
    NAME: str = "MACD"

    def __init__(self,
                 tunit: str,
                 fastperiod: int = 12,
                 slowperiod: int = 26,
                 signalperiod: int = 9) -> None:
        if (fastperiod < 1) or (slowperiod < 1) or (signalperiod < 1):
            raise ValueError()
        super().__init__(tunit)
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
        return f"{self.NAME}-{str(self._fastperiod)}-{str(self._slowperiod)}-{str(self._signalperiod)}-{self.tunit}"


class ParabolicSARIndicator(Indicator):
    NAME: str = "Parabolic SAR"

    def __init__(self, tunit: str, acceleration: float, maximum: float) -> None:
        if (acceleration < 0) or (maximum < 0):
            raise ValueError()

        super.__init__(tunit)
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
        return f"{self.NAME}-{str(self._acceleration)}-{str(self._maximum)}-{self.tunit}"


class IndicatorSet(Observer, Subject):

    def __init__(self):
        self._obs: List = []
        self._indicators: Dict[str, Indicator] = {}
        self._current_candlestick: Candlestick = None
        self._last_price: float = 0.0
        self._last_ts: str = None

    @property
    def current_candlestick(self) -> Candlestick:
        return self._current_candlestick

    @current_candlestick.setter
    def current_candlestick(self, candlestick: Candlestick) -> None:
        self._current_candlestick = candlestick

    def update(self, subject: Candlestick) -> None:
        if subject.interval in self._indicators:
            indicators_interval = self._indicators[subject.interval]

            for name, indicator_i in indicators_interval.items():
                indicator_i.update(subject)

            self._last_price = subject.close
            self._last_ts = subject.close_time
            self.notify(EventType.UPDATE, self.values())

    def attach(self, observer: Observer) -> None:
        self._obs.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._obs:
            self.obs.remove(observer)

    def notify(self) -> None:
        for observer_i in self._obs:
            observer_i.update(self)

    def add(self, interval: str, indicator: Indicator) -> None:
        name = self.indicator_description(indicator, interval)
        if name not in self._indicators:
            self._indicators[name] = indicator

    def values(self) -> Dict[str, Dict[str, Tuple | float]]:
        indicator_values = {}
        for name, indicator in self._indicators.items():
            try:
                indicator_values[name] = indicator.value()

            except Exception:
                indicator_values[name] = np.nan

        indicator_values["CLOSE_PRICE"] = self._last_price
        indicator_values["CLOSE_TIME"] = self._last_ts

        return indicator_values



