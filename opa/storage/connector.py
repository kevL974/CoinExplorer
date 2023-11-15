from abc import ABC, abstractmethod
from typing import List, Dict
from kafka import KafkaProducer
from opa.core.candlestick import Candlestick
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
    def read(self, **options) -> List:
        pass


class CsvConnector(InputOutputStream):
    def write_lines(self, candlesticks: List[Candlestick], **options) -> None:
        print(candlesticks)

    def read(self,list_files_csv: str,symbols:str, intervals:str) -> List:
        list_hbase_full = []
        for path_file in list_files_csv:
            print("Lecture du fichier: ",path_file)
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


class HbaseTableConnector(InputOutputStream):

    def __init__(self, host="localhost", port=9090, table_name="BINANCE"):
        """
        Initialize Hbase client  and create table if not already exist
        """
        self.host = host
        self.port = port
        self.table_name = table_name
        self.con = hb.Connection(self.host, self.port)
        self.__create_if_not_exist_table()

    def write_lines(self, candlesticks: List[Candlestick], **options) -> None:
        table = self.con.table(self.table_name)
        self.con.open()
        try:
            with table.batch(**options) as b:
                for candlestick in candlesticks:
                    b.put(candlestick.key(), candlestick.to_hbase())
        except ValueError as e:
            print(f"{e}")
            pass

        self.con.close()

    def read(self, **options) -> List:
        pass

    def __create_if_not_exist_table(self) -> None:
        """
        Create table with Hbase client  if not exist.
        :return:
        """
        self.con.open()
        list_tables = self.con.tables()
        if self.table_name.encode("utf-8") not in list_tables:
            self.con.create_table(self.table_name, {'CANDLESTICKES': dict(), 'TECHNICAL_INDICATORS': dict()})
        self.con.close()


class KafkaConnector(InputOutputStream):

    def __init__(self,
                 bootstrapservers: str = "localhost:9092",
                 clientid: str = "opa_collector",
                 valueserializer=lambda v: v.encode("utf-8")):
        self.kafka_producer = KafkaProducer(bootstrap_servers=bootstrapservers,
                                            client_id=clientid,
                                            value_serializer=valueserializer,
                                            api_version=(2, 8, 1))

    def write_lines(self, candlesticks: List[Candlestick], **options) -> None:
        for candlestick in candlesticks:
            self.kafka_producer.send(value=candlestick.__str__(), **options)

        self.kafka_producer.flush()

    def read(self, options) -> List:
        pass
