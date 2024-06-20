from opa.utils import *
from opa.core.candlestick import Candlestick
import pytest
import os


@pytest.mark.asyncio
async def test_csv_to_candlesticks():
    symbol = "ETHBTC"
    interval = "1m"
    file_path = "test_candlesticks.csv"
    data = [
        "1500004800000,0.08000000,0.08000000,0.08000000,0.08000000,0.04300000,1500004859999,0.00344000,1,0.00000000,0.00000000,22435.18386441\n",
        "1500004860000,0.08000000,0.08000000,0.08000000,0.08000000,0.00000000,1500004919999,0.00000000,0,0.00000000,0.00000000,22435.37386441\n",
        "1500004920000,0.08000000,0.08000000,0.08000000,0.08000000,0.30600000,1500004979999,0.02448000,2,0.00000000,0.00000000,22435.37386441\n",
        "1500004980000,0.08000000,0.08000000,0.08000000,0.08000000,0.21200000,1500005039999,0.01696000,1,0.00000000,0.00000000,22435.37386441\n",
        "1500005040000,0.08000000,0.08000000,0.08000000,0.08000000,0.16500000,1500005099999,0.01320000,2,0.00000000,0.00000000,22435.37386441\n"
    ]

    with open(file_path, "w") as file:
        file.writelines(data)

    candlesticks = await csv_to_candlesticks(symbol, interval, file_path)

    """ the number of candle sticks must be equal to the number of elements in the data list """
    assert len(data) == len(candlesticks)

    first_candlestick = candlesticks[0]
    first_line = data[0].split(',')
    first_line_open = float(first_line[1])
    first_line_high = float(first_line[2])
    first_line_low = float(first_line[3])
    first_line_close = float(first_line[4])
    first_line_volume = float(first_line[5])
    first_line_close_time = int(first_line[6])

    f""" Open price of first candlestick must be equals to  {first_line_open} """
    assert first_candlestick.open == first_line_open

    f""" High price of first candlestick must be equals to  {first_line_high} """
    assert first_candlestick.high == first_line_high

    f""" Low price of first candlestick must be equals to  {first_line_low} """
    assert first_candlestick.low == first_line_low

    f""" Close price of first candlestick must be equals to  {first_line_close} """
    assert first_candlestick.close == first_line_close

    f""" Volume of first candlestick must be equals to  {first_line_volume} """
    assert first_candlestick.volume == first_line_volume

    f""" Close  time of first candlestick must be equals to  {first_line_close_time} """
    assert first_candlestick.close_time == first_line_close_time

    os.remove(file_path)
