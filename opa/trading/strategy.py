from abc import abstractmethod
from typing import List
from opa.trading.indicator import *
from opa.trading.observer import *
import numpy as np


class TradingStrategy(ObserverInterface, ObservableInterface):

    def __init__(self):
        self._indicators = None
        self._position = None

    @property
    def position(self) -> bool:
        return self._position

    @position.setter
    def position(self, position: bool) -> None:
        self._position = position

    @property
    def indicators(self) -> IndicatorSet:
        if not self._indicators:
            self._indicators = self.make_indicators_set()
            self._indicators.add_observer(EventType.UPDATE, self)

        return self._indicators

    @abstractmethod
    def trade(self, in_position: bool, data: Dict) -> None:
        pass

    @abstractmethod
    def make_indicators_set(self) -> IndicatorSet:
        pass


class Sma200Rsi10Strategy(TradingStrategy):

    def __init__(self):
        super().__init__()
        self._wallet : Dict = {"dollars_qty": 500.0,
                               "assets_qty": 0.0}

    def make_indicators_set(self) -> IndicatorSet:
        director: Director = Director()
        builder: Builder = IndicatorSetBuilder()

        director.builder = builder
        director.build_indicators_simple_sma_rsi_strategy()
        indicator_set = builder.product
        return indicator_set

    def update(self, data: Dict) -> None:
        # TODO implement broker function to get orders.

        in_position = True
        in_position = self.trade(in_position, data)

    def add_observer(self, event_type: str, observer: ObserverInterface) -> None:
        pass

    def remove_observer(self, observer: ObserverInterface) -> None:
        pass

    def notify(self, event_type: str, data) -> None:
        if event_type == EventType.UPDATE:
            print(data)

    def trade(self, in_position: bool, data: Dict) -> None:
        print("receive new data : ")
        # for key, item in data.items():
        #     print(item.value())
        print(data)
        if not in_position:
            buy = self._wallet["dollars_qty"] * 0.05
            self._wallet["dollars_qty"] = self._wallet["dollars_qty"] - buy
            self._wallet["assets_qty"] = data["CLOSE_PRICE"] / buy
            in_position = True
            return in_position










if __name__ == "__main__":
    print("strategy")
