from __future__ import annotations

import numpy as np

from opa.AppException import UnavailableData
from opa.trading.steps.base import BaseTradingStep, logger
from opa.utils import detect_proximity, detect_rebound


class BreakingRsiNeutralLine(BaseTradingStep):

    def __init__(self, id_rsi: str):
        super().__init__()
        self._id_rsi : str = id_rsi

    def check_condition(self) -> None:
        try:

            rsi = self.context.indicator_value(self._id_rsi)
            neutral_line = np.full_like(rsi, 50.0);print("i m in BreakingRsiNeutralLine")

        except UnavailableData as e:
            logger.warning(e)
            self.on_wait()

        else:

            proximity = detect_proximity(rsi, neutral_line)[0]

            if proximity.size == 0:
                print("BreakingRsiNeutralLine fails")
                self.on_fail()
            else:
                print(rsi)
                self.on_success()

    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def on_fail(self) -> None:
        self.context.first_step()

    def on_wait(self) -> None:
        self.context.transition_to(self)


class RetestSmaStep(BaseTradingStep):

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


class PriceOnLowBollingerBdStep(BaseTradingStep):

    def __init__(self, id_bbollinger : str):
        super().__init__()
        self._id_bbollinger: str = id_bbollinger

    def check_condition(self) -> None:
        tunit = str.split(self._id_bbollinger, "-")[0]

        try:
            low_bollinger_band = self.context.indicator_value(self._id_bbollinger)[1]
            price = self.context.price_history(tunit)
            price_close = price["close"]
        except UnavailableData as e:
            logger.warning(e)
            self.on_wait()

        else :
            proximity = detect_proximity(price_close, low_bollinger_band)[0]

            if proximity.size == 0:
                print("im in Bollinger bands checking")
                self.on_fail()
            else:
                self.on_success()

    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def on_fail(self) -> None:
        self.context.first_step()

    def on_wait(self) -> None:
        self.context.transition_to(self)
