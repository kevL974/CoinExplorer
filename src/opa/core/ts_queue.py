"""Fixed-size time series queue backed by a pandas DataFrame."""
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class TsQueue:
    """Bounded FIFO queue that stores (timestamp, value) pairs as a time series.

    Internally backed by a pandas DataFrame indexed by datetime timestamps.
    When the queue exceeds `maxlen`, the oldest entries are evicted.
    """

    def __init__(self, maxlen: int = 10) -> None:
        """
        :param maxlen: maximum number of entries retained in the queue.
        """
        self._maxlen = maxlen
        self._timeseries: pd.DataFrame = pd.DataFrame(columns=["value"])
        self._timeseries.index.name = "timestamp"

    def push(self, timestamp: float, value: float) -> None:
        """Add a new (timestamp, value) entry and evict the oldest if maxlen is exceeded.

        :param timestamp: Unix timestamp in milliseconds.
        :param value: numeric value associated with the timestamp.
        """
        self._timeseries.loc[pd.to_datetime(timestamp)] = value

        if self.size() > self._maxlen:
            self._timeseries = self._timeseries.iloc[-self._maxlen:]

    def tolist(self) -> np.ndarray:
        """Return all entries as a 2-D numpy array of shape (n, 2): [[timestamp, value], ...].

        :return: numpy array with timestamp and value columns.
        """
        return self._timeseries.reset_index().to_numpy()

    def values(self) -> np.ndarray:
        """Return the value column as a 1-D numpy array.

        :return: numpy array of float values.
        """
        return self._timeseries.to_numpy().ravel()

    def timestamps(self) -> np.ndarray:
        """Return the timestamp index as a 1-D numpy array.

        :return: numpy array of datetime timestamps.
        """
        return self._timeseries.reset_index().iloc[:, 0].to_numpy().ravel()

    def earliest_value(self) -> float:
        """Return the most recent value (last entry).

        :return: float value of the latest entry.
        """
        return self._timeseries.iloc[-1, 0]

    def earliest_date(self) -> int:
        """Return the timestamp of the most recent entry (last entry).

        :return: datetime timestamp of the latest entry.
        """
        return self._timeseries.reset_index().iloc[-1, 0]

    def earliest_entry(self) -> np.ndarray:
        """Return the most recent entry as a pandas Series (timestamp, value).

        :return: pandas Series with timestamp and value.
        """
        return self._timeseries.reset_index().iloc[-1]

    def size(self) -> int:
        """Return the current number of entries in the queue.

        :return: number of entries.
        """
        return len(self._timeseries.index)

    def get_n_earliest_entry(self, n: int) -> np.ndarray:
        """Return the n most recent entries as a 2-D numpy array.

        :param n: number of most recent entries to retrieve.
        :return: numpy array of shape (n, 2) with timestamp and value columns.
        """
        return self._timeseries.iloc[-n:].reset_index().to_numpy()
