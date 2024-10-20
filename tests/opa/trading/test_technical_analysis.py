import numpy as np
import pytest
import talib

from opa.trading.technic.technical_analysis import *

close_price = [
  102.48357077,  99.30867849, 103.23844269, 107.61514928,  98.82923313,
   98.82931522, 107.89606408, 103.83717365,  97.65262807, 105.71280022,
  100.68291154, 100.67135123,  97.20981136, 100.43359878,  99.37541084,
   94.18856235,  96.9358444 ,  95.83951705, 102.6163833 ,  98.38331476,
  103.28276804, 100.88253028,  96.95868363, 101.71368281,  98.84351718,
   96.98896304, 101.2147801 , 104.63028793, 101.26800287,  94.32253697,
   99.78997727, 103.11676289, 103.31034809, 101.23413795,  96.61905955,
   96.62360597,  96.07131497, 103.7116934 , 100.56136574,  97.50953828
]

timestamps = [
  1701656707, 1701743107, 1701829507, 1701915907, 1702002307,
  1702088707, 1702175107, 1702261507, 1702347907, 1702434307,
  1702520707, 1702607107, 1702693507, 1702779907, 1702866307,
  1702952707, 1703039107, 1703125507, 1703211907, 1703298307,
  1703384707, 1703471107, 1703557507, 1703643907, 1703730307,
  1703816707, 1703903107, 1703989507, 1704075907, 1704162307,
  1704248707, 1704335107, 1704421507, 1704507907, 1704594307,
  1704680707, 1704767107, 1704853507, 1704939907, 1705026307
]

moving_avg_20 = talib.SMA(np.array(close_price),20)

@pytest.fixture()
def indicator_set() -> IndicatorSet:
    return IndicatorSet()

@pytest.mark.parametrize("tunit, indicator, expected", [
    ("4h", SmaIndicator(20), "4h-SMA-20"),
    ("4h", SmaIndicator(50), "4h-SMA-50"),
    ("1h", RsiIndicator(14), "1h-RSI-14"),
    ("15m", ParabolicSARIndicator(0.02, 0.2), "15m-SAR-0.02-0.2")
])
def test_add(indicator_set, tunit, indicator, expected):
    """
    Test if an id is created for each indicator added to IndicatorSet
    """
    indicator_set.add(tunit,indicator)
    assert expected in indicator_set._indicators[tunit].keys()
    assert expected in indicator_set._indicator_ts.keys()

@pytest.mark.parametrize("tunit, indicator", [
    ("7m", SmaIndicator(20)),
    ("2m", SmaIndicator(50))
])
def test_add_illegal_argument_raise(indicator_set, tunit, indicator):
    """
    Test if IllegalArgumentError is raised when we add an indicator to an unallowed tunit
    """
    with pytest.raises(IllegalArgumentError) as excinfo:
        indicator_set.add(tunit, indicator)

    assert str(excinfo.value) == f"IllegalArgumentError: Time unit {tunit} is not permitted"


@pytest.mark.parametrize("tunit, indicator, is_added, expected", [
    ("4h", SmaIndicator(20), True, True),
    ("4h", SmaIndicator(50), False, False),
    ("1h", RsiIndicator(14), True, True),
    ("15m", ParabolicSARIndicator(0.02, 0.2), False, False)
])
def test_indicator_exist(indicator_set, tunit, indicator, is_added, expected):
    """
    Test when we add an indicator, method indicator_exist(id) should return True
    """
    if is_added:
        indicator_set.add(tunit,indicator)

    assert indicator_set.indicator_exist(IndicatorSet.create_id(tunit, indicator)) == expected

@pytest.fixture()
def filled_indicator_set() -> IndicatorSet:
    indicator_set = IndicatorSet()
    indicator_set.add("4h", SmaIndicator(20))

    closes_ts = TsQueue(200)
    closes_ts._values_qe=close_price
    closes_ts._timestamp_qe=timestamps
    indicator_set._closes=closes_ts
@pytest.mark.skip(reason="no way of currently testing this")
def test_indicator_get_value(filled_indicator_set):

    assert moving_avg_20[-1] == filled_indicator_set.get_indicator_value("4h-SMA-20")


@pytest.fixture()
def sma_indicator() -> SmaIndicator:
    return SmaIndicator(20)

@pytest.fixture()
def closes_ts() -> np.ndarray:
    return np.array(close_price)

@pytest.fixture()
def sma_ts() -> np.ndarray:
    return np.array(moving_avg_20)

def test_sma_value(sma_indicator, closes_ts, sma_ts):
    result = sma_indicator.value(None,None,closes_ts)
    for r, e in zip(result[-20:], sma_ts[-20:]):
        print(f"result {r}, expected {e}")
    assert np.array_equal(result[-20:], sma_ts[-20:])
