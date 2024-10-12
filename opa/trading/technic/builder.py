from opa.trading.technic.step import TradingStep
from opa.trading.technic.technical_analysis import *


class Builder(ABC):

    @abstractmethod
    def set_checking_bullrun(self, tunit: str) -> None:
        pass

    @abstractmethod
    def set_checking_retest_sma100(self, tunit: str) -> None:
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

        self._builder.set_checking_bullrun(t_4h)
        self._builder.set_checking_retest_sma100(t_4h)
        self._builder.set_checking_lower_bollinger_band_breach(t_4h)
        self._builder.set_checking_sma_convergence(t_4h, SmaIndicator(20), SmaIndicator(50))
        self._builder.set_checking_rsi_break_through_neutral_line(t_4h, RsiIndicator(14))
        self._builder.set_checking_macd_bullish_crossover(t_4h, MACDIndicator(12,26,9))
        self._builder.set_checking_oversold_stochastic(t_4h, StochasticIndicator(12,3,0,3,0))
        self._builder.set_checking_oversold_stochastic(t_1h, StochasticIndicator(12, 3, 0, 3, 0))
        self._builder.set_checking_oversold_stochastic(t_15m, StochasticIndicator(12, 3, 0, 3, 0))


class IndicatorSetBuilder(Builder):

    def __init__(self) -> None:
        self._product: IndicatorSet = None
        self.reset()

    def set_checking_bullrun(self, tunit: str) -> None:
        self._product.add(tunit, SmaIndicator(20))
        self._product.add(tunit, SmaIndicator(50))
        self._product.add(tunit, RsiIndicator(14))

    def set_checking_retest_sma100(self, tunit: str) -> None:
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
        self._product = IndicatorSet()

    @property
    def product(self) -> IndicatorSet:
        product = self._product
        self.reset()
        return product


class TradingStepBuilder(Builder):

    def __init__(self) -> None:
        self._product: TradingStep = None
        self.reset()

    def set_checking_bullrun(self, tunit: str) -> None:
        pass

    def set_checking_retest_sma100(self, tunit: str) -> None:
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
        self._product = InitStep()

    @property
    def product(self) -> TradingStep:
        pass