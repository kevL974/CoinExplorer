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
        self._current_step = step
        self._current_step.context=self

    @abstractmethod
    def get_indicator_values_by_name(self, name: str) -> List:
        pass


class TradingStep(ABC):

    def __init__(self):
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

    @abstractmethod
    def on_success(self) -> None:
        pass

    @abstractmethod
    def on_fail(self) -> None:
        pass


class InitStep(TradingStep):

    def on_fail(self) -> None:
        pass

    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def check_condition(self) -> None:
        self.on_success()


class CheckBullRunStep(TradingStep):

    def __init__(self, id_sma_short: str, id_sma_long: str, id_rsi: str) -> None:
        super().__init__()
        self._id_sma_short: str = id_sma_short
        self._id_sma_long: str = id_sma_long
        self._id_rsi: str = id_rsi

    def check_condition(self) -> None:
        sma_short = self.context.get_indicator_values_by_name(self._id_sma_short)
        sma_long = self.context.get_indicator_values_by_name(self._id_sma_long)
        rsi = self.context.get_indicator_values_by_name(self._id_rsi)

        if (sma_short[-1] > sma_long[-1]) and (rsi[-1] > 50.0):
           self.on_success()
        else:
            self.on_fail()

    def on_fail(self) -> None:
        self.context.transition_to(self.context.initial_step)

    def on_success(self) -> None:
        self.context.transition_to(self.next)