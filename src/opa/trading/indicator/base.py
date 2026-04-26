import logging
from abc import ABC, abstractmethod

import numpy as np

logger = logging.getLogger(__name__)


class BaseIndicator(ABC):

    NAME: str = "BaseIndicator"

    def __init__(self, tunit):
        super().__init__()
        self.__tunit=tunit

    @abstractmethod
    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        pass

    def get_name(self) -> str:
        return self.NAME

    def tunit(self) -> str:
        return self.__tunit

    @abstractmethod
    def get_parameters(self) -> str:
        pass

    def get_id(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"{self.tunit()}_{self.get_name()}_{self.get_parameters()}"
