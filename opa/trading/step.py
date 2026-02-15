from __future__ import annotations

from os import MFD_ALLOW_SEALING

from opa.trading.context import TradingStrategy
from opa.trading.technic.analysis import *


class TradingStep(ABC):

    def __init__(self):
        self._context: TradingStrategy = None
        self._next_step: TradingStep = None

    @property
    def context(self) -> TradingStrategy:
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
        sma_short = self.context.indicator_value(self._id_sma_short)
        sma_long = self.context.indicator_value(self._id_sma_long)
        rsi = self.context.indicator_value(self._id_rsi)

        if(sma_short.ndim > 0) and (len(sma_short) > 0):
            if (sma_short > sma_long) and (rsi > 50.0):
                print(f"Check bull run : sma_short ({sma_short}) > sma_long ({sma_long} and rsi ({rsi})")
                self.on_success()
            else:
                print(f"Check bull run : sma_short ({sma_short}) < sma_long ({sma_long} and rsi ({rsi})")
                self.on_fail()

    def on_fail(self) -> None:
        self.context.first_step()

    def on_success(self) -> None:
        self.context.transition_to(self.next)


class RetestSmaStep(TradingStep):

    INIT: int = 0
    START: int = 1
    SMA_ABOVE_CONVERGENT: int = 11
    SMA_ABOVE_WAITING_DIVERGENCE: int = 12
    SMA_ABOVE_DIVERGENT: int = 13
    SMA_BELOW_CONVERGENT: int = 21
    SMA_BELOW_WAITING_DIVERGENCE: int = 22
    SMA_BELOW_DIVERGENT: int = 23
    FAIL: int = 30
    SUCCESS: int = 40

    def __init__(self, id_sma):
        super().__init__()
        self._id_sma: str = id_sma
        self._n: int = 0
        self._d: int = 0
        self._state: int = self.INIT
        self._last_price: float = 0
        self._last_sma: float = 0

    def check_condition(self) -> None:
        try :
            price = self.context.indicator_value()
            sma = self.context.indicator_value(self._id_sma)
        except ValueError:
            print(f"ReTestSmaStep - No price or sma value available")
            self.on_wait()

        if self._state == self.INIT:
            self._state = self.START

        elif self._state == self.START:
            if self.sma_converes_to_price(sma, price) and self.is_sma_above(sma, price):
                self._state = self.SMA_ABOVE_CONVERGENT
            elif self.sma_converes_to_price(sma, price) and not self.is_sma_above(sma, price):
                self._state = self.SMA_BELOW_CONVERGENT
            else:
                self._state = self.FAIL

        elif self._state == self.SMA_ABOVE_CONVERGENT:
            if not self.is_sma_above(sma, price):
                self._state = self.SMA_ABOVE_WAITING_DIVERGENCE
                self._d+=1

        elif self._state == self.SMA_BELOW_WAITING_DIVERGENCE:
            if self.is_sma_above(sma, price) and self._d < 5:
                self._state = self.SUCCESS
            elif not self.is_sma_above(sma, price) and self._d < 5:
                self._d+=1
            else:
                self._state = self.FAIL

        elif self._state == self.SMA_BELOW_CONVERGENT:
            if self.is_sma_above(sma, price):
                self._state = self.SMA_BELOW_WAITING_DIVERGENCE

        elif self._state == self.SMA_BELOW_WAITING_DIVERGENCE:
            if not self.is_sma_above(sma, price)  and self._d < 5:
                self._state = self.SUCCESS
            elif self.is_sma_above(sma, price) and self._d < 5:
                self._d+=1
            else:
                self._state = self.FAIL

        self._last_sma = sma
        self._last_price = price

        if self._state == self.FAIL:
            self.on_fail()
        elif self._state == self.SUCCESS:
            self.on_success()
        else:
            self.on_wait()

    def is_sma_above(self, sma: float, price: float) -> bool:
        return sma > price

    def diff(self, sma: float, price: float) -> float:
        if self.is_sma_above(sma, price):
            return sma - price
        return price - sma

    def sma_converes_to_price(self, current_sma: float, current_price: float) -> bool:
        return (self.diff(self._last_sma, self._last_price) - self.diff(current_sma, current_price)) > 0

    def on_wait(self) -> None:
        self.context.transition_to(self)

    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def on_fail(self) -> None:
        self.context.first_step()