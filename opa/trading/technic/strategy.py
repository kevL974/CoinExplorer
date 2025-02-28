from opa.trading.technic.step import *


class TradingStrategy(TradingContext):

    def __init__(self, initial_step: TradingStep, indicators : IndicatorSet):
        super().__init__(initial_step=initial_step)
        self._indicators: IndicatorSet = indicators

    def get_indicator_values_by_name(self, name: str) -> np.ndarray:
        pass

    @property
    def indicators(self):
        return self._indicators


class DayTradingStrategy(TradingStrategy):

    def __init__(self, initial_step: TradingStep, indicators: IndicatorSet):
        super().__init__(initial_step, indicators)

    def get_indicator_values_by_name(self, name: str) -> np.ndarray:
        return self._indicators.get_indicator_history(name)


if __name__ == "__main__":
    print("strategy")
