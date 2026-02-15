from opa.trading.step import *


class TradingStrategy:

    def __init__(self, step: TradingStep, environment: Environment):
        self._environment: Environment = environment
        self._initial_step: TradingStep = step

    @property
    def context(self):
        return self._context

    def on_receiving_candlestick(self, candlestick: Candlestick) -> None:
        self._environment.update(candlestick)


class DayTradingStrategy(TradingStrategy):

    def __init__(self, step: TradingStep, environment: Environment) -> None:
        super().__init__(step, environment)
        self._step = None
        self.transition_to(step)

    def update(self, candlestick: Candlestick) -> None:
        self._environment.put(candlestick)
        self.first_step()
        self.execute_step()

    def indicator_value(self, id_indicator: str) -> float:
        return self._environment.current_indicator_value(id_indicator)

    def price_value(self, tunit: str) -> float:
        return self._environment.current_price_value(tunit)

    def first_step(self) -> None:
        self.transition_to(self._initial_step)

    def transition_to(self, step: TradingStep) -> None:
        step.context = self
        self._step = step

    def execute_step(self):
        self._step.check_condition()


if __name__ == "__main__":
    print("strategy")
