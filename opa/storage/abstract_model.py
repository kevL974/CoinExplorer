from typing import Dict
from abc import ABC, abstractmethod


class Entity(ABC):
    """
    Simple value object to capture information
    """
    pass


class HbaseEntity(ABC,Entity):

    @abstractmethod
    def value(self) -> Dict:
        pass

    @abstractmethod
    def id(self) -> str:
        pass
