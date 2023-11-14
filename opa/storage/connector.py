from abc import ABC, abstractmethod
from typing import List
from kafka import KafkaProducer
from opa.core.candlestick import Candlestick


class InputOutputStream(ABC):

    @abstractmethod
    def write(self, data: Candlestick, **options) -> None:
        pass

    @abstractmethod
    def read(self, **options) -> List:
        pass


class CsvConnector(InputOutputStream):
    def write(self, data: Candlestick, **options) -> None:
        print(data)

    def read(self, **options) -> List:
        pass


class KafkaConnector(InputOutputStream):

    def __init__(self,
                 bootstrapservers: str = "localhost:9092",
                 clientid: str = "opa_collector",
                 valueserializer=lambda v: v.encode("utf-8")):
        self.kafka_producer = KafkaProducer(bootstrap_servers=bootstrapservers,
                                            client_id=clientid,
                                            value_serializer=valueserializer,
                                            api_version=(2, 8, 1))

    def write(self, data: Candlestick, **options) -> None:
        self.kafka_producer.send(value=data.__str__(), **options)
        self.kafka_producer.flush()

    def read(self, options) -> List:
        pass
