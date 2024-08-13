import talib
import pandas as pd
import numpy as np
from typing import List, Tuple


def simple_mobile_average(price: List, timeperiod: int) -> np.ndarray:
    """
    Calculates a simple moving average over a series of prices.
    :param price: list of price
    :param timeperiod: timeperiod for simple mobile average
    :return: list of SMA values
    """
    array_price = np.array(price)
    sma_values = talib.SMA(array_price, timeperiod=timeperiod)

    return sma_values


def exponential_mobile_average(price: List, timeperiod: int) -> List[float]:
    """
    Calculates an exponential moving average over a series of prices.
    :param price: list of price
    :param timeperiod: timeperiod for exponential mobile average
    :return: list of EMA values
    """
    array_price = np.array(price)
    exponential_values = talib.EMA(array_price, timeperiod=timeperiod)

    return exponential_values


def stochastic_relative_strength_index(price: List,
                                       timeperiod: int = 14,
                                       fastk_period: int = 5,
                                       fastd_period: int = 3) -> Tuple:
    """
    Calculates a stochastic relative strength index over a series of prices.
    :param price: list of price
    :param timeperiod: timeperiod for rsi
    :param fastk_period: k timeperiod for exponential mobile average
    :param fastd_period: d timeperiod for exponential mobile average
    :return:
    """
    np_price = np.array(price)
    stoch_rsi_k, stoch_rsi_d = talib.STOCHRSI(np_price, timeperiod=timeperiod, fastk_period=fastk_period,
                                              fastd_period=fastd_period, fastd_matype=0)
    return stoch_rsi_k, stoch_rsi_d


def relative_strength_index(price: List, timeperiod: int = 10) -> float:
    """
        Calculates a relative strength index over a series of prices.
        :param price: list of price
        :param timeperiod: timeperiod for rsi
    """
    np_price = np.array(price)
    return talib.RSI(np_price, timeperiod)


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