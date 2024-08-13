from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, TypeVar, Optional
from kafka import KafkaProducer, KafkaConsumer
from opa.core.candlestick import Candlestick
from opa.storage.repository import HbaseCrudRepository, HbaseEntity
from opa.utils import retry_connection_on_brokenpipe, retry_connection_on_ttransportexception
import pandas as pd
import happybase as hb




class InputOutputStream(ABC):

    @abstractmethod
    def write_lines(self, candlesticks: List[Candlestick], **options) -> None:
        """
        Write list of Candlestick objects to the connector
        :param candlesticks: a list of Candlestick objects
        :param options: optional parameters
        :return:
        """
        pass

    @abstractmethod
    def write(self, candlestick: Candlestick, **options) -> None:
        """
        Write a single Candlestick object to  the connector.
        :param candlestick: a Candlestick object
        :param options: optional  parameters
        :return:
        """

    @abstractmethod
    def read(self, **options) -> List:
        pass


class CsvConnector(InputOutputStream):
    def write(self, candlestick: Candlestick, **options) -> None:
        pass

    def write_lines(self, candlesticks: List[Candlestick], **options) -> None:
        print(candlesticks)

    def read(self, list_files_csv: str, symbols: str, intervals: str) -> List:
        list_hbase_full = []
        for path_file in list_files_csv:
            print("Lecture du fichier: ", path_file)
            csv = pd.read_csv(path_file, delimiter=",", header=None)
            cols = [1, 2, 3, 4, 5, 6]
            data = csv[cols]

            data.insert(0, 'Symbols', symbols[0])
            data.insert(1, 'Intervals', intervals[0])

            data_rename = data.rename(
                columns={1: "Open", 2: "High", 3: "Low", 4: "Close", 5: "Volume", 6: "Close_Time"})
            data_clean = data_rename.values.tolist()
            for ligne in data_clean:
                inser = Candlestick(ligne[0], ligne[1], ligne[2], ligne[3], ligne[4], ligne[5], ligne[6], ligne[7])
                command_hbase = inser.to_hbase()
                list_hbase_full.append(command_hbase)

        return list_hbase_full


class KafkaConnector(InputOutputStream):

    ONE_CONS_TO_ALL_TOPICS: int = 1
    ONE_CONS_TO_ONE_TOPIC: int = 0

    def __init__(self,
                 bootstrapservers: str = "localhost:9092",
                 clientid: str = "opa_collector",
                 value_serializer=lambda v: v.encode("utf-8"),
                 value_deserializer=lambda v: v.decode("utf-8"),
                 api_version=(2, 8, 1)):
        self.bootstrap_servers = bootstrapservers
        self.client_id = clientid
        self.value_serializer = value_serializer
        self.value_deserializer = value_deserializer
        self.api_version = api_version

        self.kafka_producer = KafkaProducer(bootstrap_servers=bootstrapservers,
                                            client_id=clientid,
                                            value_serializer=value_serializer,
                                            api_version=api_version)

    def write_lines(self, candlesticks: List[Candlestick], **options) -> None:
        for candlestick in candlesticks:
            self.write(candlestick, **options)

    def write(self, candlestick: Candlestick, **options) -> None:
        self.kafka_producer.send(value=candlestick.__str__(), **options)
        self.kafka_producer.flush()

    def read(self, **options) -> Dict:
        topics = options.get("topics", [])
        mode = options.get("mode", self.ONE_CONS_TO_ALL_TOPICS)
        consumers = {}
        if mode == self.ONE_CONS_TO_ALL_TOPICS:
            key = "".join(str(topic) + "_" for topic in topics)
            consumer = KafkaConsumer(bootstrap_servers=self.bootstrap_servers,
                                     client_id=self.client_id,
                                     value_deserializer=self.value_deserializer,
                                     auto_offset_reset='earliest')
            consumer.subscribe(topics)
            consumers[key] = consumer

        elif mode == self.ONE_CONS_TO_ONE_TOPIC:
            for topic_i in topics:
                consumers[topic_i] = KafkaConsumer(topics=topic_i,
                                                   bootstrap_servers=self.bootstrap_servers,
                                                   client_id=self.client_id,
                                                   value_deserializer=self.value_deserializer,
                                                   auto_offset_reset='earliest')
        else:
            raise ValueError("Bad mode argument")

        return consumers
