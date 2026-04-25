import logging

import yaml

from opa.trading.indicator.bollinger import BollingerBdIndicator
from opa.trading.indicator.macd import MACDIndicator
from opa.trading.indicator.rsi import RsiIndicator
from opa.trading.indicator.sma import SmaIndicator
from opa.trading.indicator.stochastic import StochasticIndicator

logger = logging.getLogger(__name__)

_DISPATCHER = {
    "CheckBullRun": lambda b, cfg: b.set_checking_bullrun(
        cfg["sma_short"]["tunit"],
        SmaIndicator(cfg["sma_short"]["tunit"], cfg["sma_short"]["period"]),
        SmaIndicator(cfg["sma_long"]["tunit"],  cfg["sma_long"]["period"]),
        RsiIndicator(cfg["rsi"]["tunit"],        cfg["rsi"]["period"]),
    ),
    "RetestSma": lambda b, cfg: b.set_checking_retest_sma(
        cfg["tunit"],
        SmaIndicator(cfg["tunit"], cfg["sma"]["period"]),
    ),
    "LowerBollingerBandBreach": lambda b, cfg: b.set_checking_lower_bollinger_band_breach(
        cfg["tunit"],
        BollingerBdIndicator(cfg["tunit"], **cfg["bollinger"]),
    ),
    "SmaConvergence": lambda b, cfg: b.set_checking_sma_convergence(
        cfg["tunit"],
        SmaIndicator(cfg["tunit"], cfg["sma_below"]["period"]),
        SmaIndicator(cfg["tunit"], cfg["sma_above"]["period"]),
    ),
    "RsiBreakNeutralLine": lambda b, cfg: b.set_checking_rsi_break_through_neutral_line(
        cfg["tunit"],
        RsiIndicator(cfg["tunit"], cfg["rsi"]["period"]),
    ),
    "MacdCrossAboveSignal": lambda b, cfg: b.set_checking_macd_cross_above_signal(
        cfg["tunit"],
        MACDIndicator(cfg["tunit"], **cfg["macd"]),
    ),
    "OversoldStochastic": lambda b, cfg: b.set_checking_oversold_stochastic(
        cfg["tunit"],
        StochasticIndicator(cfg["tunit"], **cfg["stochastic"]),
    ),
}


def _load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def apply_config(path: str, builder) -> None:
    """Load strategy YAML and drive builder methods in declared order."""
    data = _load_yaml(path)
    for step_cfg in data["strategy"]["steps"]:
        step_type = step_cfg["step"]
        if step_type not in _DISPATCHER:
            raise ValueError(f"Unknown step type '{step_type}' in {path}")
        _DISPATCHER[step_type](builder, step_cfg)
        logger.debug("Applied step: %s", step_type)


def get_price_history_size(path: str) -> int:
    """Return price_history_size from strategy YAML (defaults to 200)."""
    data = _load_yaml(path)
    return data["strategy"].get("price_history_size", 200)
