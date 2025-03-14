from __future__ import annotations
import numpy as np
import opa.trading.step as step
from opa.core.candlestick import Candlestick
from opa.trading.technic.analysis import IndicatorSet


class TradingContext:

    _step: step.TradingStep = None
    _initial_step: step.TradingStep = None

    def __init__(self, step: step.TradingStep, indicators: IndicatorSet) -> None:
        self._initial_step = step
        self.transition_to(step)
        self._indicators: IndicatorSet = indicators

    def update(self, candlestick: Candlestick) -> None:
        self._indicators.receive_new_candlestick(candlestick)
        self.execute_step()

    def get_indicator_values_by_name(self, name: str) -> np.ndarray:
        return self._indicators.get_indicator_history(name)

    def first_step(self) -> None:
        self.transition_to(self._initial_step)

    def transition_to(self, step: step.TradingStep) -> None:
        step.context=self
        self._step=step

    def execute_step(self):
        self._step.check_condition()