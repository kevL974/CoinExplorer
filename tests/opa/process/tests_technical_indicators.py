from opa.process.technical_indicators import simple_mobile_average, exponential_mobile_average
from typing import List
import numpy as np


def format_lists_comparaison(l1: List, l2: List) -> str:
    output = ""
    i = 0
    while (i < len(l1)) or (i < len(l2)):
        if i >= len(l1):
            l1_value = "None"
        else:
            l1_value = str(l1[i])

        if i >= len(l2):
            l2_value = "None"
        else:
            l2_value = str(l2[i])

        output += f"{l1_value}\t{l2_value}\n"
        i += 1

    return output


def test_simple_mobile_average():
    price = np.array(
        [4537.49, 4011.71, 3370.19, 3639.88, 4555.18, 4515.44, 2244.76, 1580.03, 2060.26, 4460.46, 2441.64, 3858.77,
         4776.59, 4183.71, 1406.07, 4370.87, 2947.99, 1362.47, 1741.79, 3983.69, 3729.84, 3401.18, 2632.68, 1958.12,
         2779.02, 3736.33, 1032.32, 2545.84, 3586.64, 1450.24])

    expected_sma_5 = np.array(
        [4022.89, 4018.48, 3665.09, 3307.06, 2991.13, 2972.19, 2557.43, 2880.23, 3519.54, 3944.23, 3333.36,
         3719.20, 3537.05, 2854.22, 2365.84, 2881.36, 2753.16, 2843.79, 3097.84, 3141.10, 2900.17, 2901.47,
         2427.69, 2410.33, 2736.03, 2470.27])

    expected_sma_3 = np.array(
        [3973.13, 3673.93, 3855.08, 4236.83, 3771.79, 2780.08, 1961.68, 2700.25, 2987.45, 3586.96, 3692.33,
         4273.02, 3455.46, 3320.22, 2908.31, 2893.78, 2017.42, 2362.65, 3151.77, 3704.90, 3254.57, 2663.99,
         2456.61, 2824.49, 2515.89, 2438.16, 2388.27, 2527.57])

    sma_5 = simple_mobile_average(price, 5)
    sma_5 = sma_5[~np.isnan(sma_5)]
    sma_5 = sma_5.round(2)

    sma_3 = simple_mobile_average(price, 3)
    sma_3 = sma_3[~np.isnan(sma_3)]
    sma_3 = sma_3.round(2)

    f""" Simple mobile average values for t = 5 must be {expected_sma_5} """
    assert np.array_equal(expected_sma_5, sma_5)

    f""" Simple mobile average values for t = 3 must be {expected_sma_3} """
    assert np.array_equal(expected_sma_3, sma_3)


def test_exponential_mobile_average():
    price = np.array(
        [4537.49, 4011.71, 3370.19, 3639.88, 4555.18, 4515.44, 2244.76, 1580.03, 2060.26, 4460.46, 2441.64, 3858.77,
         4776.59, 4183.71, 1406.07, 4370.87, 2947.99, 1362.47, 1741.79, 3983.69, 3729.84, 3401.18, 2632.68, 1958.12,
         2779.02, 3736.33, 1032.32, 2545.84, 3586.64, 1450.24])

    expected_ema_5 = np.array(
        [4022.89, 4018.48, 3665.09, 3307.06, 2991.13, 2972.19, 2557.43, 2880.23, 3519.54, 3944.23, 3333.36,
         3719.20, 3537.05, 2854.22, 2365.84, 2881.36, 2753.16, 2843.79, 3097.84, 3141.10, 2900.17, 2901.47,
         2427.69, 2410.33, 2736.03, 2470.27])

    expected_ema_3 = np.array(
        [3973.13, 3673.93, 3855.08, 4236.83, 3771.79, 2780.08, 1961.68, 2700.25, 2987.45, 3586.96, 3692.33,
         4273.02, 3455.46, 3320.22, 2908.31, 2893.78, 2017.42, 2362.65, 3151.77, 3704.90, 3254.57, 2663.99,
         2456.61, 2824.49, 2515.89, 2438.16, 2388.27, 2527.57])

    ema_5 = exponential_mobile_average(price, 5)
    ema_5 = ema_5[~np.isnan(ema_5)]
    ema_5 = ema_5.round(2)

    ema_3 = exponential_mobile_average(price, 3)
    ema_3 = ema_3[~np.isnan(ema_3)]
    ema_3 = ema_3.round(2)

    f""" Exponential mobile average values for t = 5 must be {expected_ema_5} """
    assert np.array_equal(expected_ema_5, ema_5)

    f""" Exponential mobile average values for t = 3 must be {expected_ema_3} """
    assert np.array_equal(expected_ema_3, ema_3)
