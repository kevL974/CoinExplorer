from typing import Dict
from abc import ABC, abstractmethod


class Entity(ABC):
    """
    Simple value object to capture information
    """
    pass


class HbaseEntity(Entity):

    @abstractmethod
    def load(self, data: Dict) -> None:
        pass

    @abstractmethod
    def value(self) -> Dict:
        pass

    @abstractmethod
    def id(self) -> str:
        pass
