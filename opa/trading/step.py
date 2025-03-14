from __future__ import annotations
from opa.trading.context import TradingContext
from opa.trading.technic.analysis import *


class TradingStep(ABC):

    def __init__(self):
        self._context: TradingContext = None
        self._next_step: TradingStep = None

    @property
    def context(self) -> TradingContext:
        return self._context

    @context.setter
    def context(self, context) -> None:
        self._context = context

    @property
    def next(self) -> TradingStep:
        return self._next_step

    @next.setter
    def next(self, step: TradingStep) -> None:
        self._next_step = step

    @abstractmethod
    def check_condition(self) -> None:
        pass

    @abstractmethod
    def on_success(self) -> None:
        pass

    @abstractmethod
    def on_fail(self) -> None:
        pass


class InitStep(TradingStep):

    def on_fail(self) -> None:
        pass

    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def check_condition(self) -> None:
        self.on_success()


class CheckBullRunStep(TradingStep):

    def __init__(self, id_sma_short: str, id_sma_long: str, id_rsi: str) -> None:
        super().__init__()
        self._id_sma_short: str = id_sma_short
        self._id_sma_long: str = id_sma_long
        self._id_rsi: str = id_rsi

    def check_condition(self) -> None:
        sma_short = self.context.get_indicator_values_by_name(self._id_sma_short)
        sma_long = self.context.get_indicator_values_by_name(self._id_sma_long)
        rsi = self.context.get_indicator_values_by_name(self._id_rsi)

        if(sma_short.ndim > 0) and (len(sma_short) > 0):
            if (sma_short[-1] > sma_long[-1]) and (rsi[-1] > 50.0):
                print(f"Check bull run : sma_short ({sma_short[-1]}) > sma_long ({sma_long[-1]} and rsi ({rsi[-1]})")
                self.on_success()
            else:
                print(f"Check bull run : sma_short ({sma_short[-1]}) < sma_long ({sma_long[-1]} and rsi ({rsi[-1]})")
                self.on_fail()

    def on_fail(self) -> None:
        self.context.first_step()

    def on_success(self) -> None:
        self.context.transition_to(self.next)


class RetestSmaStep(TradingStep):

    def __init__(self, id_sma):
        super().__init__()
        self._id_sma: str = id_sma

    def check_condition(self) -> None:
        sma = self.context.get_indicator_values_by_name(self._id_sma)
        current = self.context._indicators
        if(sma.ndim > 0) and (len(sma) > 0):


    def on_success(self) -> None:
        pass

    def on_fail(self) -> None:
        pass