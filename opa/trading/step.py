from __future__ import annotations
from opa.trading.strategy import TradingStrategy
from opa.trading.technic.analysis import *
from opa.AppException import *

import logging

from opa.utils import detect_rebound, detect_proximity

logger = logging.getLogger(__name__)


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

    @abstractmethod
    def on_wait(self) -> None:
        self.context.transition_to(self)


class InitStep(TradingStep):

    def on_wait(self) -> None:
        pass

    def on_fail(self) -> None:
        pass

    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def check_condition(self) -> None:
        self.on_success()


class CheckBullRunStep(TradingStep):

    MAX_RETRIES : int = 1400

    def __init__(self, id_sma_short: str, id_sma_long: str, id_rsi: str) -> None:
        super().__init__()
        self._id_sma_short: str = id_sma_short
        self._id_sma_long: str = id_sma_long
        self._id_rsi: str = id_rsi
        self.__nb_retries: int = 0

    def check_condition(self) -> None:
        try:
            sma_short = self.context.indicator_value(self._id_sma_short)
            sma_long = self.context.indicator_value(self._id_sma_long)
            rsi = self.context.indicator_value(self._id_rsi)
        except UnavailableData as e:
            logger.warning(e.__str__() + f" retries {self.__nb_retries}")
            if self.__nb_retries < self.MAX_RETRIES:
                self.__nb_retries += 1
                self.on_wait()
            else:
                msg = f"Can not checking condition cause indicators have issue."
                logger.error(msg)
                raise StepError(msg) from e
        else:
            self.__nb_retries = 0
            if(sma_short.ndim > 0) and (len(sma_short) > 0):
                if (sma_short[-1] > sma_long[-1]) and (rsi[-1] > 50.0).all:
                    print(f"Check bull run : sma_short ({sma_short[-1]}) > sma_long ({sma_long[-1]} and rsi ({rsi[-1]})")
                    self.on_success()
                else:
                    #print(f"Check bull run : sma_short ({sma_short[-1]}) < sma_long ({sma_long[-1]} and rsi ({rsi[-1]})")
                    self.on_fail()

    def on_fail(self) -> None:
        self.context.first_step()

    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def on_wait(self) -> None:
        pass


class RetestSmaStep(TradingStep):

    def __init__(self, id_sma):
        super().__init__()
        self._id_sma: str = id_sma

    def check_condition(self) -> None:
        tunit = str.split(self._id_sma, "-")[0]
        try :
            sma = self.context.indicator_value(self._id_sma)
            price = self.context.price_history(tunit)
            price_close = price["close"]

            rebounds = detect_rebound(price_close, sma, tolerance=0.002)[0]
            print(f"price: {price_close[-1]} --- sma: {sma[-1]}")

            if rebounds.size == 0:
                print(f"Rebound not found : {rebounds} ")
                self.on_fail()

            else :
                print(f"Rebound found : {rebounds.max()} !!! ")
                self.on_success()

        except UnavailableData:
            print(f"ReTestSmaStep - No price or sma value available")
            self.on_wait()

    def on_wait(self) -> None:
        self.context.transition_to(self)

    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def on_fail(self) -> None:
        self.context.first_step()


class PriceOnLowBollingerBdStep(TradingStep):

    def __init__(self, id_bbollinger : str):
        super().__init__()
        self._id_bbollinger: str = id_bbollinger

    def check_condition(self) -> None:
        tunit = str.split(self._id_bbollinger, "-")[0]

        try:
            low_bollinger_band = self.context.indicator_value(self._id_bbollinger)[1]
            price = self.context.price_history(tunit)
            price_close = price["close"]

            proximity = detect_proximity(price_close,low_bollinger_band)[0]

            if proximity.size == 0:
                print("im in Bollinger bands checking")
                self.on_fail()
            else:
                self.on_success()
        except UnavailableData as e:
            logger.warning(e)
            self.on_wait()



    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def on_fail(self) -> None:
        self.context.first_step()

    def on_wait(self) -> None:
        self.context.transition_to(self)