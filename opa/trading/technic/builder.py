from opa.trading.technic.technical_analysis import *


class Builder(ABC):

    @abstractmethod
    def set_sma_crossover_checker(self, sma_upSmaIndicator) -> None:
        pass

    @abstractmethod
    def produce_rsi_indicator(self, interval: str, timeperiod: int) -> None:
        pass

    @abstractmethod
    def produce_stochastic_indicator(self, interval: str, fastk_period: int, slowk_period: int, slowk_matype: int,
                                     slowd_period: int, slowd_matype: int) -> None:
        pass

    @abstractmethod
    def produce_macd_indicator(self, interval: str, fastperiod: int, slowperiod: int, signalperiod: int) -> None:
        pass

    @abstractmethod
    def produce_parabolic_sar_indicator(self, interval: str, acceleration: float, maximum: float) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @property
    @abstractmethod
    def product(self) -> None:
        pass

