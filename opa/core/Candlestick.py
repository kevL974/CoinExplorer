class Candlestick:
    def __init__(self, devise, intervalle, open_price, close_price, high, low, volume, close_time):
        self.devise = str(devise)
        self.intervalle = str(intervalle)
        self.open = float(open_price)
        self.close = float(close_price)
        self.high = float(high)
        self.low = float(low)
        self.volume = float(volume)
        self.close_time = int(close_time)

    def date(self):
        import datetime
        date = datetime.datetime.fromtimestamp(self.close_time).strftime('%Y-%m-%d')
        return date


# Exemple
candlestick = Candlestick("BTCUSDT", "15m", 4000.0, 4000.5, 4001.0, 3999.5, 10000.0, 1640805600)
print("Devise:", candlestick.devise)
print("Intervalle:", candlestick.intervalle)
print("Open:", candlestick.open)
print("Close:", candlestick.close)
print("High:", candlestick.high)
print("Low:", candlestick.low)
print("Volume:", candlestick.volume)
print("Close Time (Timestamp):", candlestick.close_time)
print(candlestick.date())
