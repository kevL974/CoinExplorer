from __future__ import annotations
from opa.trading.strategy import TradingStrategy
from opa.trading.technic.analysis import *
from typing import Tuple
from opa.AppException import *

import logging
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

    def on_wait(self) -> None:
        self.context.transition_to(self)


class InitStep(TradingStep):

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
        print("I m in Retestep")
        try :
            sma = self.context.indicator_value(self._id_sma)
            tunit = str.split(self._id_sma,"-")[0]
            price = self.context.price_history(tunit)
            price_close = price["close"]

            rebounds = self.detect_rebound(price_close,sma)[0]

            if rebounds.size == 0:
                print(f"Rebound not found : {rebounds} ")
                self.on_fail()

            else :
                print(f"Rebound found : {rebounds.max()} !!! ")
                self.on_success()

        except ValueError:
            print(f"ReTestSmaStep - No price or sma value available")
            self.on_wait()

    def detect_rebound(self, price: np.ndarray, sma: np.ndarray, tolerance: float = 0.002) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detects whether the price bounces off the 100-period SMA.

        price : np.ndarray of price values (close)
        sma   : np.ndarray of the 100-period SMA
        tolerance : relative margin (0.002 = 0.2%) used to consider a "contact"

        Returns:
            - indices where a rebound is detected
        - a boolean array indicating rebound or not
        """
        price = np.asarray(price)
        sma = np.asarray(sma)

        # 1. Proximité prix / SMA (contact)
        relative_diff = np.abs(price - sma) / sma
        contact = relative_diff < tolerance

        # 2. Rebond : prix remonte après contact
        rebound = np.zeros_like(price, dtype=bool)

        for i in range(1, len(price) - 1):
            if contact[i]:
                # prix avant > prix au contact < prix après  → forme de "V"
                if price[i] < price[i - 1] and price[i] < price[i + 1]:
                    rebound[i] = True

        indices = np.where(rebound)[0]
        return indices, rebound

    def on_wait(self) -> None:
        self.context.transition_to(self)

    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def on_fail(self) -> None:
        self.context.first_step()