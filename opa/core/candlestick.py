import datetime
import json

class Candlestick:
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

    def date(self):
        import datetime
        date = datetime.datetime.fromtimestamp(self.close_time).strftime('%Y-%m-%d')
        return date

    def key(self):
        date_key = datetime.datetime.fromtimestamp(self.close_time / 1000).strftime('%Y%m%d')
        key = self.symbol + "-" + self.interval + "#" + date_key + "#" + str(self.close_time)
        return key

    def __str__(self) -> str:
        dict_candlestick = self.__dict__
        return json.dumps(dict_candlestick)

    def to_hbase(self):
        return (self.key(), {'CANDLESTICKES:open': "'" + str(self.open) + "'",
                             'CANDLESTICKES:close': "'" + str(self.close) + "'",
                             'CANDLESTICKES:high': "'" + str(self.high) + "'",
                             'CANDLESTICKES:low': "'" + str(self.low) + "'",
                             'CANDLESTICKES:volume': "'" + str(self.volume) + "'",
                             'CANDLESTICKES:close_time': "'" + str(self.close_time) + "'"})