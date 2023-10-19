from abc import ABC, abstractmethod
from typing import List

class InputOutputStream(ABC):

    @abstractmethod
    def write(self, data, options) -> None:
        pass

    @abstractmethod
    def read(self, options) -> List:
        pass


class CsvConnector(InputOutputStream):
    def write(self, data, options) -> None:
        print(data)

    def read(self, options) -> List:
        pass