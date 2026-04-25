from abc import abstractmethod,ABC

class TradingSignal(ABC):
    """
    This class defines conditions to buy or sell assets.
    """

    @abstractmethod
    def is_buy_condition(self) -> bool:
        pass

    @abstractmethod
    def is_sell_condition(self) -> bool:
        pass