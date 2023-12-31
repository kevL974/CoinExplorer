# Exemple d'utilisation
from candlestick import Candlestick
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
