from abc import ABC, abstractmethod
import numpy as np

from opa.trading.technic.step import TradingStep


class TradingContext(ABC):

    def __init__(self, initial_step: TradingStep):
        self._current_step: TradingStep = initial_step
        self._initial_step: TradingStep = initial_step

    @property
    def initial_step(self) -> TradingStep:
        return self._initial_step

    @initial_step.setter
    def initial_step(self, step: TradingStep) -> None:
        self._initial_step = step

    @property
    def step(self) -> TradingStep:
        return self._current_step

    @step.setter
    def step(self, step: TradingStep) -> None:
        self._current_step = step

    def transition_to(self, step: TradingStep) -> None:
        self._current_step = step
        self._current_step.context=self

    @abstractmethod
    def get_indicator_values_by_name(self, name: str) -> np.ndarray:
        pass

    @property
    def current_step(self):
        return self._current_step
