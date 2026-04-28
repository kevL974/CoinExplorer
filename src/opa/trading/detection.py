"""Signal detection functions for technical analysis (rebound, proximity, convergence, crossing)."""
import logging
from typing import Tuple

import numpy as np

logger = logging.getLogger(__name__)


def detect_rebound(price: np.ndarray, indicator_values: np.ndarray,
                   tolerance: float = 0.002) -> Tuple[np.ndarray, np.ndarray]:
    """Detect candles where price bounces off an indicator (e.g. SMA) forming a V-shape.

    A rebound is detected when the price is within `tolerance` of the indicator
    and forms a local minimum (price[i-1] > price[i] < price[i+1]).

    :param price: array of close prices.
    :param indicator_values: array of indicator values (same length as price).
    :param tolerance: relative margin within which price is considered "in contact"
                      with the indicator (default 0.2%).
    :return: tuple of (indices of rebound candles, boolean mask array).
    """
    price = np.asarray(price)
    indicator_values = np.asarray(indicator_values)

    relative_diff = np.abs(price - indicator_values) / indicator_values
    contact = relative_diff < tolerance

    rebound = np.zeros_like(price, dtype=bool)

    for i in range(1, len(price) - 1):
        if contact[i]:
            if price[i] < price[i - 1] and price[i] < price[i + 1]:
                rebound[i] = True

    indices = np.where(rebound)[0]
    return indices, rebound


def detect_proximity(price: np.ndarray,
                     indicator_values: np.ndarray,
                     tolerance: float = 0.002) -> Tuple[np.ndarray, np.ndarray]:
    """Detect candles where price is at or below an indicator within a tolerance margin.

    Proximity is true when the relative difference between price and indicator
    is within `tolerance`, or when price has crossed below the indicator.

    :param price: array of close prices.
    :param indicator_values: array of indicator values (same length as price).
    :param tolerance: relative margin for proximity detection (default 0.2%).
    :return: tuple of (indices of proximity candles, boolean mask array).
    """
    price = np.asarray(price)
    indicator_values = np.asarray(indicator_values)

    relative_diff = (price - indicator_values) / indicator_values
    contact = (np.abs(relative_diff) <= tolerance) | (relative_diff <= 0)

    proximity = np.zeros_like(price, dtype=bool)

    for i in range(1, len(price) - 1):
        if contact[i]:
            proximity[i] = True

    indices = np.where(proximity)[0]
    return indices, proximity


def detect_convergence(curve_below: np.ndarray, curve_above: np.ndarray, window: int = 10) -> bool:
    """Detect whether two curves are converging over the most recent `window` candles.

    Returns True when all three conditions hold over the last window:
    - `curve_below` is strictly below `curve_above` throughout the period.
    - The distance between curves is monotonically decreasing (trend).
    - The final distance is <= 50 (absolute threshold, limit).

    :param curve_below: array of values expected to be below (e.g. short SMA).
    :param curve_above: array of values expected to be above (e.g. long SMA).
    :param window: number of most recent candles to evaluate (default 10).
    :return: True if curves are converging, False otherwise.
    """
    curve_below = np.asarray(curve_below)
    curve_above = np.asarray(curve_above)

    curve_below = curve_below[np.isfinite(curve_below)]
    curve_above = curve_above[np.isfinite(curve_above)]

    if curve_above.size <= curve_below.size:
        perimeter = curve_above.size
    else:
        perimeter = curve_below.size

    if perimeter <= window:
        window = perimeter

    is_below = np.all(curve_below[-perimeter:] < curve_above[-perimeter:])

    curve_below = curve_below[-window:]
    curve_above = curve_above[-window:]

    distance = np.abs(curve_below - curve_above)
    limit = distance[-1] <= 50
    trend = np.all(np.diff(distance) <= 0)
    logger.debug("detect_convergence: distance=%s, diff=%s, limit=%s", distance, np.diff(distance), limit)
    return bool(limit and trend and is_below)


def detect_crossing(curve_below: np.ndarray, curve_above: np.ndarray) -> bool:
    """Detect whether `curve_below` crosses above `curve_above` (bullish crossover).

    Filters NaN values before analysis. Returns True only when curve_below is
    rising overall (first value < last value) and a sign change from negative
    to positive is detected in the difference series.

    :param curve_below: array of values that should cross upward (e.g. fast MACD line).
    :param curve_above: array of values being crossed (e.g. signal line).
    :return: True if a bullish crossover is detected, False otherwise.
    :raises ValueError: if arrays have different lengths or are all NaN.
    """
    if len(curve_below) != len(curve_above):
        raise ValueError("Les listes doivent avoir la même longueur")

    mask = ~np.isnan(curve_below) & ~np.isnan(curve_above)
    if not np.any(mask):
        raise ValueError("Toutes les valeurs sont NaN")

    l1_filtered = curve_below[mask]
    l2_filtered = curve_above[mask]

    if l1_filtered[0] >= l1_filtered[-1]:
        return False

    diff = l1_filtered - l2_filtered
    sign_changes = np.diff(np.sign(diff))

    if 2 in sign_changes:
        return True

    return False
