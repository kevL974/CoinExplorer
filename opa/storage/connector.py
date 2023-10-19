from abc import ABC, abstractmethod
from typing import List, Dict


class InputOutputStream(ABC):

    @abstractmethod
    def write(self, data: Dict, options) -> None:
        pass

    @abstractmethod
    def read(self, options) -> List:
        pass


class CsvConnector(InputOutputStream):
    def write(self, data: Dict, options) -> None:
        print(data)

    def read(self, options) -> List:
        pass
