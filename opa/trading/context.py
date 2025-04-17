from __future__ import annotations
import numpy as np
import opa.trading.step as step
from opa.core.candlestick import Candlestick
from opa.trading.technic.analysis import Environment


class TradingContext:

    _step: step.TradingStep = None
    _initial_step: step.TradingStep = None

    def __init__(self, step: step.TradingStep, environment: Environment) -> None:
        self._initial_step = step
        self.transition_to(step)
        self._environment: Environment = environment

    def update(self, candlestick: Candlestick) -> None:
        self._environment.put(candlestick)
        self.execute_step()

    def indicator_history(self, id_indicator: str) -> np.ndarray:
        return self._environment.history(id_indicator)

    def first_step(self) -> None:
        self.transition_to(self._initial_step)

    def transition_to(self, step: step.TradingStep) -> None:
        step.context=self
        self._step=step

    def execute_step(self):
        self._step.check_condition()