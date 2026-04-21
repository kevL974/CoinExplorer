from __future__ import annotations

from abc import ABC, abstractmethod

from opa.trading.strategy import TradingStrategy

import logging

logger = logging.getLogger(__name__)


class BaseTradingStep(ABC):

    def __init__(self):
        self._context: TradingStrategy = None
        self._next_step: BaseTradingStep = None

    @property
    def context(self) -> TradingStrategy:
        return self._context

    @context.setter
    def context(self, context) -> None:
        self._context = context

    @property
    def next(self) -> BaseTradingStep:
        return self._next_step

    @next.setter
    def next(self, step: BaseTradingStep) -> None:
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


class InitStep(BaseTradingStep):

    def on_wait(self) -> None:
        pass

    def on_fail(self) -> None:
        pass

    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def check_condition(self) -> None:
        self.on_success()
