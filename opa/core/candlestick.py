import datetime
import json
from opa.storage.model import HbaseEntity
from typing import Dict


class Candlestick(HbaseEntity):

    def __init__(self, symbol: str, interval: str, open_price: float, close_price: float, high: float, low: float,
                 volume: float, close_time: int):
        self.symbol = symbol
        self.interval = interval
        self.open = open_price
        self.close = close_price
        self.high = high
        self.low = low
        self.volume = volume
        self.close_time = close_time

    def date(self) -> str:
        """
        Return date in string format from close time timestamps.
        :return: a date in string format 'YYYY-MM-DD'
        """
        date = datetime.datetime.fromtimestamp(self.close_time).strftime('%Y-%m-%d')
        return date

    def id(self) -> str:
        """
        Return a string used as row key in Hbase table.
        :return: a Hbase row key in string format
        """
        date_key = datetime.datetime.fromtimestamp(self.close_time / 1000).strftime('%Y%m%d')
        row_key = self.symbol + "-" + self.interval + "#" + date_key + "#" + str(self.close_time)
        return row_key

    def __str__(self) -> str:
        dict_candlestick = self.__dict__
        return json.dumps(dict_candlestick)

    def value(self) -> Dict:
        return {'CANDLESTICKS:open': "'" + str(self.open) + "'",
                'CANDLESTICKS:close': "'" + str(self.close) + "'",
                'CANDLESTICKS:high': "'" + str(self.high) + "'",
                'CANDLESTICKS:low': "'" + str(self.low) + "'",
                'CANDLESTICKS:volume': "'" + str(self.volume) + "'",
                'CANDLESTICKS:close_time': "'" + str(self.close_time) + "'"}
