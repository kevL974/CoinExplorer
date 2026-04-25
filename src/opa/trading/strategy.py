from __future__ import annotations

from opa.core.candlestick import Candlestick
from opa.trading.services import Environment
from opa.trading.steps.base import *
from opa.AppException import *
from typing import Dict

import numpy as np
import logging
logger = logging.getLogger(__name__)

class TradingStrategy(ABC):

    def __init__(self, step: BaseTradingStep, environment: Environment):
        self._environment: Environment = environment
        self._initial_step: BaseTradingStep = step

    def on_receiving_candlestick(self, candlestick: Candlestick) -> None:
        self._environment.put(candlestick)

    @abstractmethod
    def indicator_value(self, id_indicator: str) -> np.ndarray:
        pass

    @abstractmethod
    def price_value(self, tunit: str) -> Dict[str, np.ndarray]:
        pass

    @abstractmethod
    def price_history(self, tunit: str) -> Dict[str, np.ndarray]:
        pass

    @abstractmethod
    def first_step(self) -> None:
        pass

    @abstractmethod
    def transition_to(self, step: BaseTradingStep) -> None:
        pass

    @abstractmethod
    def execute_step(self):
        pass


class DayTradingStrategy(TradingStrategy):

    def __init__(self, step: BaseTradingStep, environment: Environment) -> None:
        super().__init__(step, environment)
        self._step = None
        self.first_step()

    def on_receiving_candlestick(self, candlestick: Candlestick) -> None:
        self._environment.put(candlestick)
        self.execute_step()

    def indicator_value(self, id_indicator: str) -> np.ndarray:
        try:
            indicator_value = self._environment.indicator_value(id_indicator)
        except UnavailableIndicatorData as e:
            raise UnavailableIndicatorData from e
        else:
            return indicator_value

    def price_value(self, tunit: str) -> Dict[str, float]:
        return self._environment.price_value(tunit)

    def price_history(self, tunit: str) -> Dict[str, np.ndarray]:
        try:
            history = self._environment.price_history(tunit)
        except UnavailablePriceData as e:
            msg = f"Unavailable price data for tunit {tunit}"
            logger.warning(msg)
            raise UnavailablePriceData(msg) from e
        else:
            return history

    def first_step(self) -> None:
        self.transition_to(self._initial_step)

    def transition_to(self, step: BaseTradingStep) -> None:
        step.context = self

        if step is self._initial_step:
            self._step = step

        if step is not self._step and step is not self._initial_step:
            self._step = step
            self.execute_step()

    def execute_step(self):
        try:
            self._step.check_condition()
        except StepError as e:
            logger.error(e.__str__())

