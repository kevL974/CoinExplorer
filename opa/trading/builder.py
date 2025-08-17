from opa.trading.step import TradingStep, InitStep, CheckBullRunStep, RetestSmaStep
from opa.trading.technic.analysis import *


class Builder(ABC):

    @abstractmethod
    def set_checking_bullrun(self, tunit: str, sma_short: SmaIndicator, sma_long : SmaIndicator, rsi: RsiIndicator) -> None:
        pass

    @abstractmethod
    def set_checking_retest_sma(self, tunit: str, sma: SmaIndicator) -> None:
        pass

    @abstractmethod
    def set_checking_lower_bollinger_band_breach(self, tunit: str) -> None:
        pass

    @abstractmethod
    def set_checking_sma_convergence(self, tunit: str, sma_below: SmaIndicator, sma_above: SmaIndicator) -> None:
        pass

    @abstractmethod
    def set_checking_rsi_break_through_neutral_line(self, tunit: str, rsi: RsiIndicator) -> None:
        pass

    @abstractmethod
    def set_checking_macd_bullish_crossover(self, tunit: str, macd: MACDIndicator) -> None:
        pass

    @abstractmethod
    def set_checking_oversold_stochastic(self, tunit: str, stoch: StochasticIndicator) -> None:
        pass

    @abstractmethod
    def set_checking_parabolic_sar_dots_below(self, tunit: str) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @property
    @abstractmethod
    def product(self) -> None:
        pass


class Director:

    def __init__(self):
        self._builder: Builder = None

    @property
    def builder(self) -> Builder:
        return self._builder

    @builder.setter
    def builder(self, builder: Builder) -> None:
        self._builder = builder

    def make_day_trading_strategy(self) -> None:
        t_4h = "4h"
        t_1h = "1h"
        t_15m = "15m"
        t_5m = "5m"

        self._builder.set_checking_bullrun(t_5m, SmaIndicator(t_5m,20), SmaIndicator(t_5m,50), RsiIndicator(14))
        self._builder.set_checking_retest_sma(t_4h, SmaIndicator(t_4h,100))
        self._builder.set_checking_lower_bollinger_band_breach(t_4h)
        self._builder.set_checking_sma_convergence(t_4h, SmaIndicator(t_4h,20), SmaIndicator(t_4h,50))
        self._builder.set_checking_rsi_break_through_neutral_line(t_4h, RsiIndicator(t_4h,14))
        self._builder.set_checking_macd_bullish_crossover(t_4h, MACDIndicator(t_4h,12,26,9))
        self._builder.set_checking_oversold_stochastic(t_4h, StochasticIndicator(t_4h,12,3,0,3,0))
        self._builder.set_checking_oversold_stochastic(t_1h, StochasticIndicator(t_1h,12, 3, 0, 3, 0))
        self._builder.set_checking_oversold_stochastic(t_15m, StochasticIndicator(t_15m,12, 3, 0, 3, 0))


class IndicatorSetBuilder(Builder):

    def __init__(self) -> None:
        super().__init__()
        self._product: Environment = None
        self.reset()

    def set_checking_bullrun(self, tunit: str, sma_short: SmaIndicator, sma_long : SmaIndicator, rsi: RsiIndicator) -> None:
        self._product.add_indicator(tunit, sma_short)
        self._product.add_indicator(tunit, sma_long)
        self._product.add_indicator(tunit, rsi)

    def set_checking_retest_sma(self, tunit: str, sma: SmaIndicator) -> None:
        pass

    def set_checking_lower_bollinger_band_breach(self, tunit: str) -> None:
        pass

    def set_checking_sma_convergence(self, tunit: str, sma_below: SmaIndicator, sma_above: SmaIndicator) -> None:
        pass

    def set_checking_rsi_break_through_neutral_line(self, tunit: str, rsi: RsiIndicator) -> None:
        pass

    def set_checking_macd_bullish_crossover(self, tunit: str, macd: MACDIndicator) -> None:
        pass

    def set_checking_oversold_stochastic(self, tunit: str, stoch: StochasticIndicator) -> None:
        pass

    def set_checking_parabolic_sar_dots_below(self, tunit: str) -> None:
        pass

    def reset(self) -> None:
        self._product = Environment()

    @property
    def product(self) -> Environment:
        product = self._product
        self.reset()
        return product


class TradingStepBuilder(Builder):

    def __init__(self) -> None:
        super().__init__()
        self._product: TradingStep = None
        self._current_step: TradingStep = None
        self.reset()

    def set_checking_bullrun(self, tunit: str, sma_short: SmaIndicator, sma_long : SmaIndicator, rsi: RsiIndicator) -> None:
        id_sma_short = Environment.create_id(tunit, sma_short)
        id_sma_long = Environment.create_id(tunit, sma_long)
        id_rsi = Environment.create_id(tunit, rsi)
        self._current_step.next = CheckBullRunStep(id_sma_short, id_sma_long, id_rsi)
        self._current_step = self._current_step.next

    def set_checking_retest_sma(self, tunit: str, sma: SmaIndicator) -> None:
        id_sma = Environment.create_id(tunit, sma)
        self._current_step.next = RetestSmaStep(id_sma)
        self._current_step = self._current_step.next

    def set_checking_lower_bollinger_band_breach(self, tunit: str) -> None:
        pass

    def set_checking_sma_convergence(self, tunit: str, sma_below: SmaIndicator, sma_above: SmaIndicator) -> None:
        pass

    def set_checking_rsi_break_through_neutral_line(self, tunit: str, rsi: RsiIndicator) -> None:
        pass

    def set_checking_macd_bullish_crossover(self, tunit: str, macd: MACDIndicator) -> None:
        pass

    def set_checking_oversold_stochastic(self, tunit: str, stoch: StochasticIndicator) -> None:
        pass

    def set_checking_parabolic_sar_dots_below(self, tunit: str) -> None:
        pass

    def reset(self) -> None:
        self._product = InitStep()
        self._current_step = self._product

    @property
    def product(self) -> TradingStep:
        product = self._product
        self.reset()
        return product