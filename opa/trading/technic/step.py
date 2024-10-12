from opa.trading.technic.technical_analysis import *


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
        self.step = step

    @abstractmethod
    def get_indicator_value_by_name(self, name: str) -> float:
        pass


class TradingStep(ABC):

    def __init__(self, context: TradingContext):
        self._context: TradingContext = context
        self._next_step: TradingStep = None

    @property
    def context(self) -> TradingContext:
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


class InitStep(TradingStep):

    def check_condition(self) -> None:
        self.context.transition_to()


class CheckBullRunStep(TradingStep):

    def check_condition(self) -> None:
        self.context.get_indicator_value_by_name()