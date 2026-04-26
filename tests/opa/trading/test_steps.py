import numpy as np

from opa.core.candlestick import Candlestick
from opa.trading.services import Environment
from opa.trading.strategy import DayTradingStrategy
from opa.trading.steps.base import InitStep, BaseTradingStep
from opa.trading.steps.crossing import (
    BreakingRsiNeutralLine, RetestSmaStep, PriceOnLowBollingerBdStep, MacdCrossAboveSignalStep
)
from opa.trading.steps.trend import CheckBullRunStep, OversoldStochasticStep
from opa.trading.indicator.bollinger import BollingerBdIndicator
from opa.trading.indicator.macd import MACDIndicator
from opa.trading.indicator.rsi import RsiIndicator
from opa.trading.indicator.sma import SmaIndicator
from opa.trading.indicator.stochastic import StochasticIndicator
from tests.conftest import TerminalStep, fill_environment


SMA_SHORT_ID = "5m-5m_SMA_20"
SMA_LONG_ID  = "5m-5m_SMA_50"
RSI_ID       = "5m-5m_RSI_14"
STOCH_ID     = "5m-5m_Stochastic_5#3#3"
BOLLINGER_ID = "5m-5m_BOLLINGER_20#2#2#0"
MACD_ID      = "5m-5m_MACD_12#26#9"


def run_step(step_under_test: BaseTradingStep, env: Environment):
    """Wire InitStep → step_under_test → TerminalStep, execute once, return strategy."""
    terminal = TerminalStep()
    step_under_test.next = terminal
    init = InitStep()
    init.next = step_under_test
    strategy = DayTradingStrategy(init, env)
    strategy.execute_step()
    return strategy, init, terminal


def make_env(indicators, closes, interval="5m"):
    """Create a real Environment, register indicators, fill with closes."""
    env = Environment()
    for ind in indicators:
        env.indicators_manager.add(interval, ind)
    fill_environment(env, closes, interval)
    return env


class TestCheckBullRunStep:

    def test_success_on_bull_trend(self, filled_environment):
        step = CheckBullRunStep(SMA_SHORT_ID, SMA_LONG_ID, RSI_ID)
        strategy, init, terminal = run_step(step, filled_environment)
        assert strategy._step is terminal

    def test_wait_on_empty_environment(self):
        env = Environment()
        step = CheckBullRunStep(SMA_SHORT_ID, SMA_LONG_ID, RSI_ID)
        strategy, init, terminal = run_step(step, env)
        assert strategy._step is step  # on_wait() → stays

    def test_fail_on_bear_trend(self):
        closes = np.linspace(200.0, 100.0, 200)
        env = make_env(
            [SmaIndicator("5m", 20), SmaIndicator("5m", 50), RsiIndicator("5m", 14)],
            closes,
        )
        step = CheckBullRunStep(SMA_SHORT_ID, SMA_LONG_ID, RSI_ID)
        strategy, init, terminal = run_step(step, env)
        assert strategy._step is init  # on_fail() → reset to initial

    def test_fail_when_bull_sma_but_rsi_below_50(self):
        """sma_short > sma_long (rebond récent) mais RSI < 50 (déclin en cours) → doit échouer."""
        # flat(150) → hausse 100→200(30) → baisse 200→180(20)
        # sma_short(20) ≈ 190 > sma_long(50) ≈ 166, mais RSI ≈ 0 après 20 bougies baissières
        closes = np.concatenate([
            np.full(150, 100.0),
            np.linspace(100.0, 200.0, 30),
            np.linspace(200.0, 180.0, 20),
        ])
        env = make_env(
            [SmaIndicator("5m", 20), SmaIndicator("5m", 50), RsiIndicator("5m", 14)],
            closes,
        )
        step = CheckBullRunStep(SMA_SHORT_ID, SMA_LONG_ID, RSI_ID)
        strategy, init, terminal = run_step(step, env)
        assert strategy._step is init  # rsi < 50 → on_fail()


class TestBreakingRsiNeutralLine:

    def test_success_when_rsi_oscillates_near_50(self):
        t = np.arange(200)
        closes = 150.0 + 5.0 * np.sin(t * 0.5)  # oscillating → RSI crosses 50
        env = make_env([RsiIndicator("5m", 14)], closes)
        step = BreakingRsiNeutralLine(RSI_ID)
        strategy, init, terminal = run_step(step, env)
        assert strategy._step is terminal

    def test_fail_on_strong_bull_trend(self, filled_environment):
        step = BreakingRsiNeutralLine(RSI_ID)
        strategy, init, terminal = run_step(step, filled_environment)
        assert strategy._step is init  # RSI >> 50, no proximity → on_fail()

    def test_wait_on_empty_environment(self):
        env = Environment()
        step = BreakingRsiNeutralLine(RSI_ID)
        strategy, init, terminal = run_step(step, env)
        assert strategy._step is step  # UnavailableData → on_wait()


class TestOversoldStochasticStep:

    def test_success_when_oversold(self):
        n = 200
        env = Environment()
        env.indicators_manager.add("5m", StochasticIndicator("5m", 5, 3, 0, 3, 0))
        for i in range(n):
            cs = Candlestick(
                "BTCUSDT", "5m",
                91.0, 91.0,    # open, close
                110.0, 90.0,   # high, low — close near the bottom → stochastic < 10
                1000.0,
                1700000000 + i * 300,
            )
            env.put(cs)
        step = OversoldStochasticStep(STOCH_ID)
        strategy, init, terminal = run_step(step, env)
        assert strategy._step is terminal

    def test_fail_on_bull_trend(self, filled_environment):
        step = OversoldStochasticStep(STOCH_ID)
        strategy, init, terminal = run_step(step, filled_environment)
        assert strategy._step is init  # stochastic not oversold in uptrend → on_fail()

    def test_wait_on_empty_environment(self):
        env = Environment()
        step = OversoldStochasticStep(STOCH_ID)
        strategy, init, terminal = run_step(step, env)
        assert strategy._step is step


class TestRetestSmaStep:

    def test_success_on_rebound(self):
        # 197 bougies à 10000, puis V : 10010 → 9990 → 10010
        # SMA(20)≈10000, 9990 est dans la tolérance de 0.2% et forme un V → rebound détecté
        closes = np.concatenate([np.full(197, 10000.0), [10010.0, 9990.0, 10010.0]])
        env = make_env([SmaIndicator("5m", 20)], closes)
        step = RetestSmaStep(SMA_SHORT_ID)
        strategy, init, terminal = run_step(step, env)
        assert strategy._step is terminal

    def test_fail_on_bull_trend(self, filled_environment):
        # Tendance haussière : prix toujours >3% au-dessus du SMA → pas de contact → pas de rebound
        step = RetestSmaStep(SMA_SHORT_ID)
        strategy, init, terminal = run_step(step, filled_environment)
        assert strategy._step is init

    def test_wait_on_empty_environment(self):
        env = Environment()
        step = RetestSmaStep(SMA_SHORT_ID)
        strategy, init, terminal = run_step(step, env)
        assert strategy._step is step


class TestPriceOnLowBollingerBdStep:

    def test_success_when_price_below_lower_band(self):
        # 198 bougies à 100, puis drop brutal à 50 (index 198), 100 (index 199)
        # lower_band(20) ≈ 75.7 à l'index 198 → prix 50 < lower_band → proximity = True
        closes = np.concatenate([np.full(198, 100.0), [50.0, 100.0]])
        env = make_env([BollingerBdIndicator("5m", 20, 2, 2, 0)], closes)
        step = PriceOnLowBollingerBdStep(BOLLINGER_ID)
        strategy, init, terminal = run_step(step, env)
        assert strategy._step is terminal

    def test_fail_on_bull_trend(self, filled_environment):
        # Prix bien au-dessus de la bande basse → pas de proximité → on_fail()
        step = PriceOnLowBollingerBdStep(BOLLINGER_ID)
        strategy, init, terminal = run_step(step, filled_environment)
        assert strategy._step is init

    def test_wait_on_empty_environment(self):
        env = Environment()
        step = PriceOnLowBollingerBdStep(BOLLINGER_ID)
        strategy, init, terminal = run_step(step, env)
        assert strategy._step is step


class TestMacdCrossAboveSignalStep:

    def test_success_on_slow_down_then_fast_up(self):
        # Descente lente (150 bougies) puis montée rapide (50 bougies) :
        # MACD part négatif, signal suit avec retard → croisement net au pivot → True
        closes = np.concatenate([np.linspace(200.0, 100.0, 150), np.linspace(100.0, 400.0, 50)])
        env = make_env([MACDIndicator("5m", 12, 26, 9)], closes)
        step = MacdCrossAboveSignalStep(MACD_ID)
        strategy, init, terminal = run_step(step, env)
        assert strategy._step is terminal

    def test_fail_on_bull_trend(self, filled_environment):
        # Tendance haussière pure : MACD ≈ signal constants, detect_crossing = False → on_fail()
        step = MacdCrossAboveSignalStep(MACD_ID)
        strategy, init, terminal = run_step(step, filled_environment)
        assert strategy._step is init

    def test_wait_on_empty_environment(self):
        env = Environment()
        step = MacdCrossAboveSignalStep(MACD_ID)
        strategy, init, terminal = run_step(step, env)
        assert strategy._step is step
