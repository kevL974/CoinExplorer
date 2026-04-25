import numpy as np
import pytest

from opa.core.candlestick import Candlestick
from opa.trading.services import Environment
from opa.trading.strategy import DayTradingStrategy
from opa.trading.steps.base import InitStep, BaseTradingStep
from opa.trading.steps.crossing import BreakingRsiNeutralLine
from opa.trading.steps.trend import CheckBullRunStep, OversoldStochasticStep
from opa.trading.indicator.rsi import RsiIndicator
from opa.trading.indicator.sma import SmaIndicator
from opa.trading.indicator.stochastic import StochasticIndicator
from tests.conftest import TerminalStep, fill_environment


SMA_SHORT_ID = "5m-5m_SMA_20"
SMA_LONG_ID  = "5m-5m_SMA_50"
RSI_ID       = "5m-5m_RSI_14"
STOCH_ID     = "5m-5m_Stochastic_5#3#3"


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
