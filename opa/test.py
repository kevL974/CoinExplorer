import os.path
from os import listdir,pardir
import pandas as pd
from typing import List, Dict, Any

from core.candlestick import Candlestick
import happybase as hb
import sys

from pandas import Series, DataFrame




def hbase(data_csv: list):
    con = hb.Connection("172.17.0.2",9090)

    con.open()
    if con.tables() == "":
        con.create_table('BINANCE', {'CANDLESTICKES': dict(), 'TECHNICAL_INDICATORS': dict()})
        table = con.table("BINANCE")
        print(con.tables())

    for ligne in data_csv:
        table.put(ligne)




def read(list_files_csv: str,symbols:str, intervals:str) -> List:
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
            line_hbase = (inser.key(), {'CANDLESTICKES:open': inser.open,
                        'CANDLESTICKES:close': inser.close,
                        'CANDLESTICKES:high': inser.high,
                        'CANDLESTICKES:low': inser.low,
                        'CANDLESTICKES:volume': inser.volume,
                        'CANDLESTICKES:close_time': inser.close_time})
            lines = str(line_hbase)
            lines = lines.replace("': ", "': '")
            lines = lines.replace(", '", "', '")
            line_hbase = lines.replace("}", "'}")

            print(line_hbase)
            list_hbase_full.append(line_hbase)

    print(list_hbase_full)
    return list_hbase_full

list_files_csv = ['C:\\Users\\arnau\\Repo_GIT\\SEPT23-BDE-OPA\\opa\\harvest\\data/spot/monthly/klines/BTCUSDT/1m/extract\\BTCUSDT-1m-2017-08.csv']
csv = (['BTCUSDT', '1m', 4261.48, 4261.48, 4261.48, 4261.48, 1.775183, 1502942459999],
           ['BTCUSDT', '1m', 4261.48, 4261.48, 4261.48, 4261.48, 0.0, 1502942519999],
           ['BTCUSDT', '1m', 4724.89, 4724.89, 4724.89, 4724.89, 0.0, 1504224059999],
           ['BTCUSDT', '1m', 4689.89, 4689.91, 4689.89, 4689.91, 0.422439, 1504224119999],
           ['BTCUSDT', '1m',4689.91, 4689.91, 4689.91, 4689.91, 0.0, 1504224179999],
           ['BTCUSDT', '1m', 4689.91, 4689.91, 4689.91, 4689.91, 0.0, 1504224239999],
           ['BTCUSDT', '1m', 4689.91, 4689.91, 4689.91, 4689.91, 0.0, 1504224299999],
           ['BTCUSDT', '1m', 4725.0, 4725.0, 4725.0, 4725.0, 0.47356, 1504224359999],
           ['BTCUSDT', '1m', 4725.0, 4725.0, 4725.0, 4725.0, 0.0, 1504224419999],
           ['BTCUSDT', '1m', 4378.49, 4378.49, 4378.49, 4378.49, 0.891882, 1506816059999])
#list_hbase = read(list_files_csv,["BTCUSDT"],["1m"])
hbase(list_files_csv)