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
    def set_checking_sma_convergence(self, tunit: str, sma_below: int, sma_above: int) -> None:
        pass

    @abstractmethod
    def set_checking_rsi_break_through_neutral_line(self, tunit: str, rsi: float) -> None:
        pass

    @abstractmethod
    def set_checking_macd_bullish_crossover(self, tunit: str, macd: float) -> None:
        pass

    @abstractmethod
    def set_checking_oversold_stochastic(self, tunit: str, stoch: float) -> None:
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

