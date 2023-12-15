import os.path
from os import listdir,pardir
import pandas as pd
from typing import List, Dict, Any

from core.candlestick import Candlestick
import happybase as hb
import sys

from pandas import Series, DataFrame

class HbaseConnector():

    def __init__(self,host="localhost",port=9090, table = "BINANCE3"):
        """
        Initialisation du client HBase
        """
        self.host = host
        self.port = port
        self.table = table
        self.con = hb.Connection(self.host, self.port)

    def check_table(self):
        table_exist = bool
        list_table = self.con.tables()
        for table in list_table:
            if self.table == table:
                table_exist == True

        if table_exist != True:
            self.con.create_table(self.table, {'CANDLESTICKES': dict(), 'TECHNICAL_INDICATORS': dict()})
            table = self.con.table(self.table)




    def write(self, candlesticks: List, **options) -> None:
        """
        utiliser le client  hbase pour inserer les données
        :param data:
        :param options:
        :return:
        """


        self.con.create_table(self.table, {'CANDLESTICKES': dict(), 'TECHNICAL_INDICATORS': dict()})
        table = self.con.table(self.table)
        self.con.open()
        print(self.con)

        for data in candlesticks:
            # data = 'BTCUSDT-1m#20170817#1502942459999',{'CANDLESTICKES:open': '4261.48', 'CANDLESTICKES:close': 4261.48, 'CANDLESTICKES:high': '4261.48', 'CANDLESTICKES:low': '4261.48', 'CANDLESTICKES:volume': '1.775183', 'CANDLESTICKES:close_time': '1502942459999'}
            print(data)
            self.table.put(data[0], data[1])

    def read(self, **options) -> List:
        pass

toto = HbaseConnector()
toto.write(Candlestick)