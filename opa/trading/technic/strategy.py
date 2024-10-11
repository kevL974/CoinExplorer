from opa.trading.technic.step import *


class TradingStrategy(TradingContext):

    def __init__(self, initial_step: TradingStep, indicators : IndicatorSet):
        super().__init__(initial_step=initial_step)
        self._indicators: IndicatorSet = indicators

    def get_indicator_value_by_name(self, name: str) -> float:
        self.


if __name__ == "__main__":
    print("strategy")
