from abc import ABC, abstractmethod
from typing import List, Dict
from kafka import KafkaProducer
from opa.core.candlestick import Candlestick
import pandas as pd


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

    def read(self,list_files_csv: str,symbols:str, intervals:str) -> List:
        list_hbase_full = []

        for path_file in list_files_csv:

            csv = pd.read_csv(path_file, delimiter=",", header=None)
            cols = [1, 2, 3, 4, 5, 6]
            data = csv[cols]
            print(path_file)
            data.insert(0, 'Symbols', symbols[0])
            data.insert(1, 'Intervals', intervals[0])

            data_rename = data.rename(
                columns={1: "Open", 2: "High", 3: "Low", 4: "Close", 5: "Volume", 6: "Close_Time"})
            data_clean = data_rename.values.tolist()
            for ligne in data_clean:
                inser = Candlestick(ligne[0], ligne[1], ligne[2], ligne[3], ligne[4], ligne[5], ligne[6], ligne[7])
                list_hbase = (inser.key(), {'CANDLESTICKES:open': inser.open,
                                            'CANDLESTICKES:close': inser.close,
                                            'CANDLESTICKES:high': inser.high,
                                            'CANDLESTICKES:low': inser.low,
                                            'CANDLESTICKES:volume': inser.volume,
                                            'CANDLESTICKES:close_time': inser.close_time})
                list_hbase_full.append(list_hbase)

        return list_hbase_full


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
