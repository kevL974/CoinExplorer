from abc import ABC, abstractmethod
from typing import List, Dict
import numpy as np
from opa.utils import TsQueue
from opa.core.candlestick import Candlestick
from opa.trading.observer import ObserverInterface, ObservableInterface, EventType
from opa.process.technical_indicators import simple_mobile_average, relative_strength_index


class Indicator(ABC):

    @abstractmethod
    def update(self, candlestick: Candlestick) -> None:
        pass

    @abstractmethod
    def value(self) -> float:
        pass


class SmaIndicator(Indicator):
    NAME: str = "SMA"

    def __init__(self, period: int) -> None:
        if period < 1:
            raise ValueError()
        self._period = period
        self._window = TsQueue(maxlen=self._period)

    def update(self, candlestick: Candlestick) -> None:
        self._window.append(ts=candlestick.close_time, value=candlestick.close)

    def value(self) -> float:
        close_time, close_price = self._window.tolist()
        return simple_mobile_average(price=close_price, timeperiod=self._period)

    def __str__(self) -> str:
        return self.NAME + str(self._period)


class RsiIndicator(Indicator):
    NAME: str = "RSI"

    def __init__(self, period: int) -> None:
        if period < 1:
            raise ValueError()
        self._period = period
        self._window = TsQueue(maxlen=self._period +1)

    def update(self, candlestick: Candlestick) -> None:
        self._window.append(ts=candlestick.close_time, value=candlestick.close)

    def value(self) -> float:
        close_time, close_price = self._window.tolist()
        return relative_strength_index(close=close_price, timeperiod=self._period)

    def __str__(self) -> str:
        return self.NAME + str(self._period)


class IndicatorSet(ObserverInterface, ObservableInterface):

    def __init__(self):
        self._obs: Dict = {}
        self._indicators: Dict[str, Indicator] = {}
        self._last_price: float = 0.0
        self._last_ts: str = None

    def update(self, candlestick: Candlestick) -> None:
        for name, indicator_i in self._indicators.items():
            indicator_i.update(candlestick)

        self._last_price = candlestick.close
        self._last_ts = candlestick.close_time
        self.notify(EventType.UPDATE, self.values())

    def add_observer(self, event_type: str, observer: ObserverInterface) -> None:
        if event_type not in self._obs:
            self._obs[event_type] = []

        self._obs[event_type].append(observer)

    def remove_observer(self, observer: ObserverInterface) -> None:
        for event_type, observers in self._obs:
            if observer in observers:
                observers.remove(observer)

    def notify(self, event_type: str, data) -> None:
        if event_type in self._obs:
            event_type_observers = self._obs[event_type]
            for observer_i in event_type_observers:
                observer_i.update(data)

    def add(self, indicator: Indicator) -> None:
        if not indicator.__str__() in self._indicators:
            self._indicators[indicator.__str__()] = indicator

    def values(self) -> Dict[str, float]:
        indicators_values = {}
        for ind_name, ind_i in self._indicators.items():
            indicators_values[ind_name] = ind_i.value()

        indicators_values["CLOSE_PRICE"] = self._last_price
        indicators_values["CLOSE_TIME"] = self._last_ts

        return indicators_values


class Builder(ABC):

    @abstractmethod
    def produce_sma_indicator(self, timeperiod: int) -> None:
        pass

    @abstractmethod
    def produce_rsi_indicator(self, timeperiod: int) -> None:
        pass

    @abstractmethod
    def reset(self) -> IndicatorSet:
        pass

    @property
    @abstractmethod
    def product(self) -> None:
        pass


class IndicatorSetBuilder(Builder):

    def __init__(self):
        self._indicator_set = None
        self.reset()

    @property
    def product(self) -> IndicatorSet:
        indicator_set = self._indicator_set
        self.reset()
        return indicator_set

    def reset(self) -> IndicatorSet:
        self._indicator_set = IndicatorSet()

    def produce_sma_indicator(self, timeperiod: int) -> None:
        self._indicator_set.add(SmaIndicator(timeperiod))

    def produce_rsi_indicator(self, timeperiod: int) -> None:
        self._indicator_set.add(RsiIndicator(timeperiod))


class Director:

    def __init__(self) -> None:
        self._builder: Builder = None

    @property
    def builder(self) -> Builder:
        return self._builder

    @builder.setter
    def builder(self, builder: Builder) -> None:
        self._builder = builder

    def build_indicators_simple_sma_rsi_strategy(self):
        self._builder.produce_rsi_indicator(10)
        self._builder.produce_sma_indicator(200)
