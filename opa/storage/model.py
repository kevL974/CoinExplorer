from typing import Dict, List
from abc import ABC, abstractmethod


class Entity(ABC):
    """
    Simple value object to capture information
    """
    pass


class HbaseEntity(Entity):

    @abstractmethod
    def value(self) -> Dict:
        """
        Return a dictionary that maps all object attributs with theirs values in order to be saved inside a Hbase
        database.
        :return: a Dict with values in string format
        """
        pass

    @abstractmethod
    def id(self) -> str:
        pass


class Asset(HbaseEntity):

    def __init__(self, name: str, intervals: List[str]):
        assert len(intervals) != 0
        self.name = name
        self.intervals = intervals

    def value(self) -> Dict:
        value = " ".join(self.intervals)
        return {'MARKET_DATA:interval': "'" + str(value) + "'"}

    def id(self) -> str:
        return self.name
