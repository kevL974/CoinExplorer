import pytest
from opa.trading.technic.technical_analysis import *

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
    assert expected in indicator_set._indicators
    assert expected in indicator_set._indicator_ts

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