from __future__ import annotations

import numpy as np

from opa.AppException import UnavailableData
from opa.trading.steps.base import BaseTradingStep, logger
from opa.utils import detect_proximity, detect_rebound, detect_crossing


class BreakingRsiNeutralLine(BaseTradingStep):

    def __init__(self, id_rsi: str):
        super().__init__()
        self._id_rsi : str = id_rsi

    def check_condition(self) -> None:
        try:

            rsi = self.context.indicator_value(self._id_rsi)
            neutral_line = np.full_like(rsi, 50.0)
            logger.debug("BreakingRsiNeutralLine: checking RSI proximity to neutral line")

        except UnavailableData as e:
            logger.warning(e)
            self.on_wait()

        else:

            proximity = detect_proximity(rsi, neutral_line)[0]

            if proximity.size == 0:
                logger.debug("BreakingRsiNeutralLine: no proximity found, failing")
                self.on_fail()
            else:
                logger.info("BreakingRsiNeutralLine: RSI near neutral line, succeeding")
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
            logger.debug("RetestSmaStep: price=%.4f, sma=%.4f", price_close[-1], sma[-1])

            if rebounds.size == 0:
                logger.debug("RetestSmaStep: no rebound found, failing")
                self.on_fail()

            else:
                logger.info("RetestSmaStep: rebound found at index %d", rebounds.max())
                self.on_success()

        except UnavailableData:
            logger.warning("RetestSmaStep: no price or sma value available")
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
            low_bollinger_band = self.context.indicator_value(self._id_bbollinger)[2]
            price = self.context.price_history(tunit)
            price_close = price["close"]
        except UnavailableData as e:
            logger.warning(e)
            self.on_wait()

        else :
            proximity = detect_proximity(price_close, low_bollinger_band)[0]

            if proximity.size == 0:
                logger.debug("PriceOnLowBollingerBdStep: price not near lower band, failing")
                self.on_fail()
            else:
                self.on_success()

    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def on_fail(self) -> None:
        self.context.first_step()

    def on_wait(self) -> None:
        self.context.transition_to(self)


class MacdCrossAboveSignalStep(BaseTradingStep):

    def __init__(self, id_macd):
        super().__init__()
        self._id_macd: str = id_macd

    def check_condition(self) -> None:

        try:
            macd, signal, hist = self.context.indicator_value(self._id_macd)

            if detect_crossing(macd, signal):
                logger.info("MacdCrossAboveSignalStep: MACD crossed above signal")
                self.on_success()
            else:
                logger.debug("MacdCrossAboveSignalStep: no MACD crossover detected, failing")
                self.on_fail()
        except UnavailableData as e:
            logger.warning(e)
            self.on_wait()

    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def on_fail(self) -> None:
        self.context.first_step()

    def on_wait(self) -> None:
        self.context.transition_to(self)