from talib import stream
import pandas as pd
import numpy as np
from typing import List, Tuple


def simple_mobile_average(price: List, timeperiod: int) -> float:
    """
    Calculates a simple moving average over a series of prices.
    :param price: list of price
    :param timeperiod: timeperiod for simple mobile average
    :return: Latest SMA value
    """
    array_price = np.array(price)
    sma_values = stream.SMA(array_price, timeperiod=timeperiod)

    return sma_values


def exponential_mobile_average(close: List, timeperiod: int) -> float:
    """
    Calculates an exponential moving average over a series of prices.
    :param close: list of price
    :param timeperiod: timeperiod for exponential mobile average
    :return: latest EMA value
    """
    array_price = np.array(close)
    exponential_values = stream.EMA(array_price, timeperiod=timeperiod)

    return exponential_values


def stochastic_relative_strength_index(close: List, timeperiod: int = 14, fastk_period: int = 5,
                                       fastd_period: int = 3) -> Tuple:
    """
    Calculates a stochastic relative strength index over a series of prices.
    :param close: list of price
    :param timeperiod: timeperiod for rsi
    :param fastk_period: k timeperiod for exponential mobile average
    :param fastd_period: d timeperiod for exponential mobile average
    :return:
    """
    np_price = np.array(close)
    stoch_rsi_k, stoch_rsi_d = stream.STOCHRSI(np_price, timeperiod=timeperiod, fastk_period=fastk_period,
                                              fastd_period=fastd_period, fastd_matype=0)
    return stoch_rsi_k, stoch_rsi_d


def relative_strength_index(close: List, timeperiod: int = 10) -> float:
    """
        Calculates a relative strength index over a series of prices.
        :param close: list of price
        :param timeperiod: timeperiod for rsi
        :return: Latest RSI value
    """
    np_price = np.array(close)
    return stream.RSI(np_price, timeperiod)


def stochastic(high: List, low: List, close: List, timeperiod: int = 10) -> float:
    stream.STOCH()


if __name__ == '__main__':
    price = [float(x) for x in range(0, 200, 1)]
    price2 = [float(x) for x in range(10, 150, 2)]
    price2.reverse()
    price.extend(price2)

    timeperiod = 5

    sma = simple_mobile_average(price, timeperiod)
    ema = exponential_mobile_average(price, timeperiod)
    stch_rsi = stochastic_relative_strength_index(price)
    print(sma)
    print(ema)
    print(stch_rsi)