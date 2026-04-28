import os
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from opa.core.ts_queue import TsQueue
from opa.core.conversion import csv_to_candlesticks


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

def test_tsqueue_push():
    tsQueue = TsQueue(200)
    ts = datetime.now().timestamp()
    value = 12
    tsQueue.push(ts, value)

    """ size must be equals to 1 after push """
    assert tsQueue.size() == 1

    ts_values = zip([i for i in range(201)],[datetime.now().timestamp()+i for i in range(201)], strict=True)

    for x in ts_values:
        tsQueue.push(x[0],x[1])

    """ size must be equals to 200 after 201 push """
    assert tsQueue.size() == 200

def test_tsqueue_tolist():
    tsQueue = TsQueue(200)
    ts_0 = datetime.now().timestamp()
    value_0 = 12
    ts_1 = ts_0 + 200
    value_1 = 21
    tsQueue.push(ts_0, value_0)
    tsQueue.push(ts_1, value_1)

    result=np.array([[pd.to_datetime(ts_0), value_0], [pd.to_datetime(ts_1), value_1]])

    f""" tsQueue.tolist() {tsQueue.tolist().__str__()} must be equals to result {result}"""
    assert np.array_equal(tsQueue.tolist(), result)

def test_tsqueue_earliest_entry():
    tsQueue = TsQueue(200)
    ts = datetime.now().timestamp()
    value = 12
    tsQueue.push(ts, value)

    earliest_ts = ts + 200
    earliest_value = 21
    tsQueue.push(earliest_ts, earliest_value)

    result = np.array([pd.to_datetime(earliest_ts), earliest_value])

    f""" tsQueue.tolist() {tsQueue.earliest_entry().__str__()} must be equals to result {result}"""
    assert np.array_equal(tsQueue.earliest_entry(), result)

def test_tsqueue_earliest_value():
    tsQueue = TsQueue(200)
    ts = datetime.now().timestamp()
    value = 12
    tsQueue.push(ts, value)

    earliest_ts = ts+200
    earliest_value = 21
    tsQueue.push(earliest_ts, earliest_value)

    f""" tsQueue.tolist() {tsQueue.earliest_value().__str__()} must be equals to result {earliest_value}"""
    assert tsQueue.earliest_value() == earliest_value

def test_tsqueue_earliest_date():
    tsQueue = TsQueue(200)
    ts = datetime.now().timestamp()
    value = 12
    tsQueue.push(ts, value)

    earliest_ts = ts+200
    earliest_value = 21
    tsQueue.push(earliest_ts, earliest_value)

    f""" tsQueue.tolist() {tsQueue.earliest_date().__str__()} must be equals to result {earliest_ts}"""
    assert tsQueue.earliest_date() == pd.to_datetime(earliest_ts)

def test_tsqueue_earliest_n_entry():
    tsQueue = TsQueue(15)
    ts_serie = [datetime.now().timestamp() + i for i in range(18)]
    value_serie = [i for i in range(18)]
    ts_values = zip(ts_serie, value_serie, strict=True)

    for ts, value in ts_values:
        tsQueue.push(ts, value)

    result = np.array([[pd.to_datetime(ts_serie[15]), value_serie[15]],[pd.to_datetime(ts_serie[16]), value_serie[16]],[pd.to_datetime(ts_serie[17]), value_serie[17]]])

    f""" tsQueue.tolist() {tsQueue.get_n_earliest_entry(3).__str__()} must be equals to result {result}"""
    assert np.array_equal(tsQueue.get_n_earliest_entry(3), result)

def test_tsqueue_values():
    tsQueue = TsQueue(20)
    values = 30000 + np.cumsum(np.random.normal(2, 10, 20))
    dates = pd.date_range(start="2024-01-01", periods=20, freq="4h").to_numpy()

    ts_values = zip(dates, values, strict=True)

    for ts, value in ts_values:
        tsQueue.push(ts, value)

    expected = values

    f"""TsQueue.values() must be equals to expected {expected}"""
    assert np.array_equal(tsQueue.values(), expected)