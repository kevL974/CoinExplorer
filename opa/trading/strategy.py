from opa.trading.step import *


class TradingStrategy:

    def __init__(self, context: TradingContext):
        self._context: TradingContext = context

    @property
    def context(self):
        return self._context

    def on_receiving_candlestick(self, candlestick: Candlestick) -> None:
        self._context.update(candlestick)


class DayTradingStrategy(TradingStrategy):

    def __init__(self, context: TradingContext):
        super().__init__(context)


if __name__ == "__main__":
    print("strategy")
