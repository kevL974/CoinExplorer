import numpy as np
import pytest
import talib

from opa.trading.indicator.sma import SmaIndicator
from opa.trading.indicator.rsi import RsiIndicator
from opa.trading.indicator.macd import MACDIndicator
from opa.trading.indicator.bollinger import BollingerBdIndicator
from opa.trading.indicator.stochastic import StochasticIndicator
from opa.trading.indicator.parabolic_sar import ParabolicSARIndicator


class TestSmaIndicator:

    def test_returns_correct_shape(self, price_arrays):
        ind = SmaIndicator("5m", 20)
        result = ind.value(None, None, price_arrays["closes"])
        assert result.shape == price_arrays["closes"].shape

    def test_last_values_not_nan(self, price_arrays):
        ind = SmaIndicator("5m", 20)
        result = ind.value(None, None, price_arrays["closes"])
        assert not np.any(np.isnan(result[-20:]))

    def test_matches_talib(self, price_arrays):
        ind = SmaIndicator("5m", 20)
        result = ind.value(None, None, price_arrays["closes"])
        expected = talib.SMA(price_arrays["closes"], timeperiod=20)
        np.testing.assert_array_equal(result, expected)

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError):
            SmaIndicator("5m", 0)

    def test_get_id(self):
        assert SmaIndicator("5m", 20).get_id() == "5m_SMA_20"


class TestRsiIndicator:

    def test_returns_correct_shape(self, price_arrays):
        ind = RsiIndicator("5m", 14)
        result = ind.value(None, None, price_arrays["closes"])
        assert result.shape == price_arrays["closes"].shape

    def test_bull_trend_rsi_high(self, price_arrays):
        ind = RsiIndicator("5m", 14)
        result = ind.value(None, None, price_arrays["closes"])
        assert result[-1] > 50

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError):
            RsiIndicator("5m", 0)

    def test_get_id(self):
        assert RsiIndicator("5m", 14).get_id() == "5m_RSI_14"


class TestMACDIndicator:

    def test_returns_three_arrays(self, price_arrays):
        ind = MACDIndicator("5m", 12, 26, 9)
        macd, signal, hist = ind.value(None, None, price_arrays["closes"])
        assert macd.shape == price_arrays["closes"].shape
        assert signal.shape == price_arrays["closes"].shape
        assert hist.shape == price_arrays["closes"].shape

    def test_invalid_fast_period_raises(self):
        with pytest.raises(ValueError):
            MACDIndicator("5m", 0, 26, 9)

    def test_get_id(self):
        assert MACDIndicator("5m", 12, 26, 9).get_id() == "5m_MACD_12#26#9"


class TestBollingerBdIndicator:

    def test_returns_three_arrays(self, price_arrays):
        ind = BollingerBdIndicator("5m", 20, 2, 2, 0)
        upper, middle, lower = ind.value(None, None, price_arrays["closes"])
        assert upper.shape == price_arrays["closes"].shape

    def test_upper_above_lower(self, price_arrays):
        ind = BollingerBdIndicator("5m", 20, 2, 2, 0)
        upper, middle, lower = ind.value(None, None, price_arrays["closes"])
        assert np.all(upper[-100:] >= lower[-100:])

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError):
            BollingerBdIndicator("5m", 10, 2, 2, 0)  # period < 20

    def test_get_id(self):
        assert BollingerBdIndicator("5m", 20, 2, 2, 0).get_id() == "5m_BOLLINGER_20#2#2#0"


class TestStochasticIndicator:

    def test_returns_two_arrays(self, price_arrays):
        ind = StochasticIndicator("5m", 5, 3, 0, 3, 0)
        slowk, slowd = ind.value(
            price_arrays["highs"], price_arrays["lows"], price_arrays["closes"]
        )
        assert slowk.shape == price_arrays["closes"].shape
        assert slowd.shape == price_arrays["closes"].shape

    def test_oversold_on_flat_low_price(self):
        n = 200
        highs  = np.full(n, 110.0)
        lows   = np.full(n, 90.0)
        closes = np.full(n, 91.0)  # price near the bottom of range
        ind = StochasticIndicator("5m", 5, 3, 0, 3, 0)
        slowk, slowd = ind.value(highs, lows, closes)
        assert np.all(slowk[-5:] < 20)
        assert np.all(slowd[-5:] < 20)

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError):
            StochasticIndicator("5m", 0, 3, 0, 3, 0)

    def test_get_id(self):
        assert StochasticIndicator("5m", 5, 3, 0, 3, 0).get_id() == "5m_Stochastic_5#3#3"


class TestParabolicSARIndicator:

    def test_returns_correct_shape(self, price_arrays):
        sar = ParabolicSARIndicator("5m", acceleration=0.02, maximum=0.2)
        result = sar.value(price_arrays["highs"], price_arrays["lows"], price_arrays["closes"])
        assert result.shape == price_arrays["closes"].shape

    def test_parameters_affect_output(self, price_arrays):
        """Acceleration et maximum doivent réellement influer sur le calcul talib."""
        sar_slow = ParabolicSARIndicator("5m", acceleration=0.02, maximum=0.2)
        sar_fast = ParabolicSARIndicator("5m", acceleration=0.10, maximum=0.4)
        result_slow = sar_slow.value(price_arrays["highs"], price_arrays["lows"], price_arrays["closes"])
        result_fast = sar_fast.value(price_arrays["highs"], price_arrays["lows"], price_arrays["closes"])
        assert not np.allclose(result_slow, result_fast, equal_nan=True)

    def test_invalid_params_raise(self):
        with pytest.raises(ValueError):
            ParabolicSARIndicator("5m", acceleration=-0.1, maximum=0.2)
        with pytest.raises(ValueError):
            ParabolicSARIndicator("5m", acceleration=0.02, maximum=-0.1)

    def test_get_id(self):
        assert ParabolicSARIndicator("5m", 0.02, 0.2).get_id() == "5m_SAR_0.02#0.2"
