from abc import ABC, abstractmethod
from typing import List, Dict
from kafka import KafkaProducer
from opa.core.candlestick import Candlestick
import pandas as pd
import happybase as hb


class InputOutputStream(ABC):

    @abstractmethod
    def write_lines(self, candlesticks: List[Candlestick], **options) -> None:
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


class HbaseConnector(InputOutputStream):

    def __init__(self,host="localhost",port=9090, table = "BINANCE3"):
        """
        Initialisation du client HBase
        """
        self.host = host
        self.port = port
        self.table = table
        self.con = hb.Connection(self.host, self.port)

    def write_lines(self, candlesticks: List[Candlestick], **options) -> None:
        """
        utiliser le client  hbase pour inserer les données
        :param candlesticks:
        :param options:
        :return:
        """
        self.con.create_table(self.table, {'CANDLESTICKES': dict(), 'TECHNICAL_INDICATORS': dict()})
        self.table = self.con.table(self.table)
        self.con.open()
        print(self.con)

        for candlestick in candlesticks:
            # data = 'BTCUSDT-1m#20170817#1502942459999',{'CANDLESTICKES:open': '4261.48', 'CANDLESTICKES:close': 4261.48, 'CANDLESTICKES:high': '4261.48', 'CANDLESTICKES:low': '4261.48', 'CANDLESTICKES:volume': '1.775183', 'CANDLESTICKES:close_time': '1502942459999'}
            print(candlestick)
            self.table.put(candlestick[0], candlestick[1])

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

    def write_lines(self, candlesticks: List[Candlestick], **options) -> None:
        for candlestick in candlesticks:
            self.kafka_producer.send(value=candlestick.__str__(), **options)

        self.kafka_producer.flush()

    def read(self, options) -> List:
        pass
