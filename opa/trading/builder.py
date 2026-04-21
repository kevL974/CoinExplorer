from opa.trading.indicator.bollinger import BollingerBdIndicator
from opa.trading.indicator.macd import MACDIndicator
from opa.trading.indicator.rsi import RsiIndicator
from opa.trading.indicator.sma import SmaIndicator
from opa.trading.indicator.stochastic import StochasticIndicator
from opa.trading.services import Environment
from opa.trading.steps.base import BaseTradingStep, InitStep
from opa.trading.steps.crossing import BreakingRsiNeutralLine, RetestSmaStep, PriceOnLowBollingerBdStep, \
    MacdCrossAboveSignalStep
from opa.trading.steps.trend import CheckBullRunStep, ConvergingMovingAverages, OversoldStochasticStep
from opa.trading.indicator.base import *


class Builder(ABC):

    @abstractmethod
    def set_checking_bullrun(self, tunit: str, sma_short: SmaIndicator, sma_long : SmaIndicator, rsi: RsiIndicator) -> None:
        pass

    @abstractmethod
    def set_checking_retest_sma(self, tunit: str, sma: SmaIndicator) -> None:
        pass

    @abstractmethod
    def set_checking_lower_bollinger_band_breach(self, tunit: str, bollinger_bands : BollingerBdIndicator) -> None:
        pass

    @abstractmethod
    def set_checking_sma_convergence(self, tunit: str, sma_below: SmaIndicator, sma_above: SmaIndicator) -> None:
        pass

    @abstractmethod
    def set_checking_rsi_break_through_neutral_line(self, tunit: str, rsi: RsiIndicator) -> None:
        pass

    @abstractmethod
    def set_checking_macd_cross_above_signal(self, tunit: str, macd: MACDIndicator) -> None:
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

        self._builder.set_checking_bullrun(t_5m, SmaIndicator(t_5m, 20), SmaIndicator(t_5m, 50), RsiIndicator(t_5m, 14))
        self._builder.set_checking_retest_sma(t_15m, SmaIndicator(t_15m, 100))
        self._builder.set_checking_lower_bollinger_band_breach(t_5m, BollingerBdIndicator(t_5m))
        self._builder.set_checking_sma_convergence(t_15m, SmaIndicator(t_15m, 20), SmaIndicator(t_15m, 50))
        self._builder.set_checking_rsi_break_through_neutral_line(t_5m, RsiIndicator(t_5m, 14))
        self._builder.set_checking_macd_cross_above_signal(t_4h, MACDIndicator(t_4h, 12, 26, 9))
        self._builder.set_checking_oversold_stochastic(t_4h, StochasticIndicator(t_4h, 12, 3, 0, 3, 0))
        self._builder.set_checking_oversold_stochastic(t_1h, StochasticIndicator(t_1h, 12, 3, 0, 3, 0))
        self._builder.set_checking_oversold_stochastic(t_15m, StochasticIndicator(t_15m, 12, 3, 0, 3, 0))


class EnvironmentSetBuilder(Builder):

    def __init__(self) -> None:
        super().__init__()
        self._product: Environment = None
        self.reset()

    def set_checking_bullrun(self, tunit: str, sma_short: SmaIndicator, sma_long : SmaIndicator, rsi: RsiIndicator) -> None:
        self._product.add_indicator(tunit, sma_short)
        self._product.add_indicator(tunit, sma_long)
        self._product.add_indicator(tunit, rsi)

    def set_checking_retest_sma(self, tunit: str, sma: SmaIndicator) -> None:
        self._product.add_indicator(tunit, sma)

    def set_checking_lower_bollinger_band_breach(self, tunit: str, bollinger_bands : BollingerBdIndicator) -> None:
        self._product.add_indicator(tunit, bollinger_bands)

    def set_checking_sma_convergence(self, tunit: str, sma_below: SmaIndicator, sma_above: SmaIndicator) -> None:
        self._product.add_indicator(tunit, sma_below)
        self._product.add_indicator(tunit, sma_above)

    def set_checking_rsi_break_through_neutral_line(self, tunit: str, rsi: RsiIndicator) -> None:
        self._product.add_indicator(tunit, rsi)

    def set_checking_macd_cross_above_signal(self, tunit: str, macd: MACDIndicator) -> None:
        self._product.add_indicator(tunit,macd)

    def set_checking_oversold_stochastic(self, tunit: str, stoch: StochasticIndicator) -> None:
        self._product.add_indicator(tunit, stoch)

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
        self._product: BaseTradingStep = None
        self._current_step: BaseTradingStep = None
        self.reset()

    def set_checking_bullrun(self, tunit: str, sma_short: SmaIndicator, sma_long : SmaIndicator, rsi: RsiIndicator) -> None:
        id_sma_short = Environment.create_identifier(tunit, sma_short)
        id_sma_long = Environment.create_identifier(tunit, sma_long)
        id_rsi = Environment.create_identifier(tunit, rsi)
        self._current_step.next = CheckBullRunStep(id_sma_short, id_sma_long, id_rsi)
        self._current_step = self._current_step.next

    def set_checking_retest_sma(self, tunit: str, sma: SmaIndicator) -> None:
        id_sma = Environment.create_identifier(tunit, sma)
        self._current_step.next = RetestSmaStep(id_sma)
        self._current_step = self._current_step.next

    def set_checking_lower_bollinger_band_breach(self, tunit: str, bollinger_bands : BollingerBdIndicator) -> None:
        id_bollinger_bands = Environment.create_identifier(tunit, bollinger_bands)
        self._current_step.next = PriceOnLowBollingerBdStep(id_bollinger_bands)
        self._current_step = self._current_step.next

    def set_checking_sma_convergence(self, tunit: str, sma_below: SmaIndicator, sma_above: SmaIndicator) -> None:
        id_sma_below = Environment.create_identifier(tunit, sma_below)
        id_sma_above = Environment.create_identifier(tunit, sma_above)
        self._current_step.next = ConvergingMovingAverages(id_sma_below, id_sma_above)
        self._current_step = self._current_step.next

    def set_checking_rsi_break_through_neutral_line(self, tunit: str, rsi: RsiIndicator) -> None:
        id_rsi = Environment.create_identifier(tunit, rsi)
        self._current_step.next = BreakingRsiNeutralLine(id_rsi)
        self._current_step = self._current_step.next

    def set_checking_macd_cross_above_signal(self, tunit: str, macd: MACDIndicator) -> None:
        id_macd = Environment.create_identifier(tunit, macd)
        self._current_step.next = MacdCrossAboveSignalStep(id_macd)
        self._current_step = self._current_step.next

    def set_checking_oversold_stochastic(self, tunit: str, stoch: StochasticIndicator) -> None:
        id_stoch = Environment.create_identifier(tunit, stoch)
        self._current_step.next = OversoldStochasticStep(id_stoch)
        self._current_step = self._current_step.next

    def set_checking_parabolic_sar_dots_below(self, tunit: str) -> None:
        pass

    def reset(self) -> None:
        self._product = InitStep()
        self._current_step = self._product

    @property
    def product(self) -> BaseTradingStep:
        product = self._product
        self.reset()
        return product