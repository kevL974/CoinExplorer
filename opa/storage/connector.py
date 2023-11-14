from abc import ABC, abstractmethod
from typing import List, Dict
import pandas as pd
import happybase as hb
from opa.core.candlestick import Candlestick


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

    def __init__(self):
        """
        Initialisation du client HBase
        """
        con = hb.Connection("hbase-docker", 9090)
        con.open()

    def write(self, candlesticks: List,tables  : str, **options) -> None:
        """
        utiliser le client  hbase pour inserer les données
        :param data:
        :param options:
        :return:
        """
        self.con.create_tables('BINANCE', {'CANDLESTICKES': dict(), 'TECHNICAL_INDICATORS': dict()})
        table = self.con.tables("BINANCE")
        for data in candlesticks:
            # data = 'BTCUSDT-1m#20170817#1502942459999',{'CANDLESTICKES:open': '4261.48', 'CANDLESTICKES:close': 4261.48, 'CANDLESTICKES:high': '4261.48', 'CANDLESTICKES:low': '4261.48', 'CANDLESTICKES:volume': '1.775183', 'CANDLESTICKES:close_time': '1502942459999'}
            table.put(data[0], data[1])

    def read(self, **options) -> List:
        pass