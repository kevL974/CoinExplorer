from opa.trading.builder import Builder
from opa.trading.step import *


class IndicatorSetBuilder(Builder):

    def __init__(self):
        self._indicator_set = None
        self.reset()

    @property
    def product(self) -> Environment:
        indicator_set = self._indicator_set
        self.reset()
        return indicator_set

    def reset(self) -> Environment:
        self._indicator_set = Environment()

    def set_sma_crossover_checker(self, tunit1: str, tperiod1: int, tunit2: str, tperiod2: int) -> None:
        self._indicator_set.add(tunit1, SmaIndicator(tperiod1))
        self._indicator_set.add(tunit2, SmaIndicator(tperiod2))


class TradingStateBuilder(Builder):

    def __init__(self):
        self._initial_state: TradingState = None
        self._current_state: TradingState = self._initial_state
        self.reset()

    def reset(self) -> None:
        self._initial_state = SearchBullishTrend()
        self._current_state = self._initial_state

    def set_sma_crossing_check(self, tunit_sma_up: str, tperiod1_sma_up: int, tunit_sma: str,
                                  tperiod_sma: int) -> None:
        state = SmaCrossingCheck(tunit_sma_up, tperiod1_sma_up, tunit_sma, tperiod_sma)
        self._current_state.set_next_state(state)
        self._current_state = state

    def set_rsi_above_neutral_line_check(self, tunit_rsi: str, tperiod_rsi: int) -> None:
        state =


# def produce_sma_indicator(self, interval: str, timeperiod: int) -> None:
#     self._indicator_set.add(interval, SmaIndicator(timeperiod))
#
# def produce_rsi_indicator(self, interval: str, timeperiod: int) -> None:
#     self._indicator_set.add(interval, RsiIndicator(timeperiod))
#
# def produce_stochastic_indicator(self, interval: str, fastk_period: int, slowk_period: int, slowk_matype: int,
#                                  slowd_period: int, slowd_matype: int) -> None:
#     self._indicator_set.add(interval, StochasticIndicator(fastk_period=fastk_period,
#                                                           slowk_period=slowk_period,
#                                                           slowk_matype=slowk_matype,
#                                                           slowd_period=slowd_period,
#                                                           slowd_matype=slowd_matype))
#
# def produce_macd_indicator(self, interval: str, fastperiod: int, slowperiod: int, signalperiod: int) -> None:
#     self._indicator_set.add(interval, MACDIndicator(fastperiod=fastperiod,
#                                                     slowperiod=slowperiod,
#                                                     signalperiod=signalperiod))
#
# def produce_parabolic_sar_indicator(self, interval: str, acceleration: float, maximum: float) -> None:
#     self._indicator_set.add(interval, ParabolicSARIndicator(acceleration=acceleration, maximum=maximum))


class Director:

    def __init__(self) -> None:
        self._builder: Builder = None

    @property
    def builder(self) -> Builder:
        return self._builder

    @builder.setter
    def builder(self, builder: Builder) -> None:
        self._builder = builder

    def build_indicators_simple_sma_rsi_strategy(self):
        self._builder.produce_rsi_indicator("5m", 10)
        self._builder.produce_sma_indicator("5m", 200)

    def build_indicators_swing_trading(self):
        # unit 4H
        self._builder.produce_sma_indicator("4h", 100)

        # unit 5m
        self._builder.produce_sma_indicator("5m", 20)
        self._builder.produce_sma_indicator("5m", 50)
        self._builder.produce_rsi_indicator("5m", 14)
        self._builder.produce_macd_indicator("5m", 12, 26, 9)
        self._builder.produce_parabolic_sar_indicator("5m", 0.02, 0.2)
        self._builder.produce_stochastic_indicator("5m", 12, 3, 0, 3, 0)

        # unit 15m
        self._builder.produce_sma_indicator("15m", 20)
        self._builder.produce_sma_indicator("15m", 50)
        self._builder.produce_rsi_indicator("15m", 14)
        self._builder.produce_macd_indicator("15m", 12, 26, 9)
        self._builder.produce_parabolic_sar_indicator("15m", 0.02, 0.2)
        self._builder.produce_stochastic_indicator("15m", 12, 3, 0, 3, 0)

        # unit 1h
        self._builder.produce_sma_indicator("1h", 20)
        self._builder.produce_sma_indicator("1h", 50)
        self._builder.produce_rsi_indicator("1h", 14)
        self._builder.produce_macd_indicator("1h", 12, 26, 9)
        self._builder.produce_parabolic_sar_indicator("1h", 0.02, 0.2)
        self._builder.produce_stochastic_indicator("1h", 12, 3, 0, 3, 0)
