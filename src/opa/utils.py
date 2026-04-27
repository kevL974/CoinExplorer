import logging
from os.path import basename, dirname, join, realpath
from typing import Callable, Dict, List, Tuple
from zipfile import BadZipfile

import aiocsv
import numpy as np
import pandas as pd
from aiofiles import open as aio_open
from aiofiles.os import listdir
from aiofiles.ospath import isdir
from async_unzip.unzipper import unzip
from thriftpy2.transport.base import TTransportException

from opa.core.candlestick import Candlestick
from opa.harvest.ochlv_constant import (
    IDX_CLOSE,
    IDX_CLOSE_TIME,
    IDX_HIGHT,
    IDX_LOW,
    IDX_OPEN,
    IDX_VOLUME,
    KEY_CLOSE,
    KEY_CLOSE_TIME,
    KEY_HIGHT,
    KEY_LOW,
    KEY_OPEN,
    KEY_SYMBOL,
    KEY_VOLUME,
)

logger = logging.getLogger(__name__)


def hist_klines_websocket_to_candlestick(symbol: str, interval: str, klines: List[str]) -> Candlestick:
    """
    Convert klines to candlestick object.
    :param interval: time period of candlestick
    :param klines: OCHLV in list representation
    :return: c
    """
    return Candlestick(symbol, interval,
                       open_price=float(klines[IDX_OPEN]),
                       close_price=float(klines[IDX_CLOSE]),
                       high=float(klines[IDX_HIGHT]),
                       low=float(klines[IDX_LOW]),
                       volume=float(klines[IDX_VOLUME]),
                       close_time=int(klines[IDX_CLOSE_TIME]))


def stream_klines_to_candlestick(interval, klines: Dict) -> Candlestick:
    """
    Convert klines from websocket to candlestick object.
    :param interval: time period of candlestick
    :param klines: OCHLV in list representation
    :return: time period of candlestick
    """

    return Candlestick(symbol=klines[KEY_SYMBOL],
                       interval=interval,
                       open_price=klines[KEY_OPEN],
                       close_price=klines[KEY_CLOSE],
                       high=klines[KEY_HIGHT],
                       low=klines[KEY_LOW],
                       volume=klines[KEY_VOLUME],
                       close_time=klines[KEY_CLOSE_TIME])


async def csv_to_candlesticks(symbol: str, interval: str, csv_filepath: str) -> List[Candlestick]:
    """
    Read csv file that contents candlesticks and  transforms them to list Candlestick object.
    :param symbol: symbol of candlestick in csv file
    :param interval: interval of candlestick in csv file
    :param csv_filepath: path to csv file
    :return: a list of Candlestick object
    """
    candlesticks = []
    try:
        async with aio_open(csv_filepath, mode='r', newline='\n') as csvfile:
            async for row in aiocsv.AsyncReader(csvfile, delimiter=','):
                candlesticks.append(Candlestick(symbol=symbol,
                                                interval=interval,
                                                open_price=float(row[1]),
                                                high=float(row[2]),
                                                low=float(row[3]),
                                                close_price=float(row[4]),
                                                volume=float(row[5]),
                                                close_time=int(row[6])))
    except FileNotFoundError:
        logger.error("CSV file '%s' not found", csv_filepath)

    return candlesticks


def dict_to_candlesticks(msg: Dict) -> Candlestick:
    """
    Candlestick in dictionnary format to Candlestick object.
    :param msg: a dictionnary with Candlestick attibuts as keys.
    :return: a Candlestick object.
    """
    return Candlestick(symbol=msg["symbol"],
                       interval=msg["interval"],
                       open_price=float(msg["open"]),
                       close_price=float(msg["close"]),
                       high=float(msg["high"]),
                       low=float(msg["low"]),
                       volume=float(msg["volume"]),
                       close_time=int(msg["close_time"]))


async def list_file(directory_path: str, extension: str) -> List[str]:
    """
    Returns the list of files to unzip present in the directory indicated in the variable directory_path.
    :param directory_path: Targerted directory
    :return: list of path.
    """
    files = []
    all_files_in_directory = await listdir(directory_path)
    for file in all_files_in_directory:
        if (file.find(extension) >= 0) & (not await isdir(file)):
            files.append(file)
        else:
            logger.debug("Skipping non-%s file: %s", extension, file)
    return files


async def dezip(zip_path: str) -> str:
    """
    Uncompresses zip file given in parameter
    :param zip_path: zip file to be uncompressed.
    :return:
    """
    pwd = dirname(realpath(__file__))
    zip_absolut_path = join(pwd, zip_path)
    try:
        await unzip(zip_absolut_path,  join(dirname(zip_absolut_path), "extract"))
    except BadZipfile as e:
        logger.error("%s : %s", e, zip_absolut_path)

    return join(dirname(zip_absolut_path), "extract", basename(zip_path).replace('zip', 'csv'))


def is_valid_connection_setting_format(connection_settings: str) -> bool:
    if connection_settings:
        return ":" in connection_settings
    return False


def parse_connection_settings(connection_settings: str) -> Tuple[str, int]:
    """
    Parse connection settings in string  format
    :param connection_settings: a string like '<host>:<port>'
    :return: return Tuple(host,port)
    """
    if not is_valid_connection_setting_format(connection_settings):
        raise ValueError(f"Bad connection settings {connection_settings}")

    settings = connection_settings.split(":")
    host = settings[0]
    port = int(settings[1])
    return host, port


def retry_connection_on_brokenpipe(max_retries: int = 5):
    if max_retries <= 0:
        raise ValueError(f"max_retries must be > 0 instead of {max_retries}")

    def retry_connection(function: Callable):
        def retry(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return function(*args, **kwargs)
                except BrokenPipeError:
                    logger.warning("Try n°%d failed, retry...", retries + 1)
                    retries += 1
            raise Exception("Maximum retries exceeded")

        return retry

    return retry_connection


def retry_connection_on_ttransportexception(max_retries: int = 5):
    if max_retries <= 0:
        raise ValueError(f"max_retries must be > 0 instead of {max_retries}")

    def retry_connection(function: Callable):
        def retry(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return function(*args, **kwargs)
                except TTransportException:
                    logger.warning("Try n°%d failed, retry...", retries + 1)
                    retries += 1
            raise Exception("Maximum retries exceeded")

        return retry

    return retry_connection

def detect_rebound(price: np.ndarray, indicator_values: np.ndarray,
                   tolerance: float = 0.002) -> Tuple[np.ndarray, np.ndarray]:
    """
    Detects whether the price bounces off the 100-period SMA.

    price : np.ndarray of price values (close)
    sma   : np.ndarray of the 100-period SMA
    tolerance : relative margin (0.002 = 0.2%) used to consider a "contact"

    Returns:
        - indices where a rebound is detected
        - a boolean array indicating rebound or not
    """
    price = np.asarray(price)
    indicator_values = np.asarray(indicator_values)

    # 1. Proximité prix / SMA (contact)
    relative_diff = np.abs(price - indicator_values) / indicator_values
    contact = relative_diff < tolerance

    # 2. Rebond : prix remonte après contact
    rebound = np.zeros_like(price, dtype=bool)

    for i in range(1, len(price) - 1):
        if contact[i]:
            # prix avant > prix au contact < prix après  → forme de "V"
            if price[i] < price[i - 1] and price[i] < price[i + 1]:
                rebound[i] = True

    indices = np.where(rebound)[0]
    return indices, rebound


def detect_proximity(price: np.ndarray,
                     indicator_values: np.ndarray,
                     tolerance: float = 0.002) -> Tuple[np.ndarray, np.ndarray]:

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
    curve_below = np.asarray(curve_below)
    curve_above = np.asarray(curve_above)

    curve_below = curve_below[np.isfinite(curve_below)]
    curve_above = curve_above[np.isfinite(curve_above)]

    if curve_above.size <= curve_below.size :
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
    
    if 2 in sign_changes :
        return True
    
    return False

class TsQueue:

    def __init__(self, maxlen: int = 10) -> None:
        self._maxlen = maxlen
        self._timeseries: pd.DataFrame = pd.DataFrame(columns=["value"])
        self._timeseries.index.name="timestamp"

    def push(self, timestamp: float, value: float) -> None:
        """
        Adds a new timeserie value and checks if the size of the queue is exceeded,
        if yes then the function deletes the elements at the index above maxlen
        :param timestamp: an integer
        :param value: a float
        :return: None
        """
        self._timeseries.loc[pd.to_datetime(timestamp)]=value

        if self.size() > self._maxlen:
            self._timeseries = self._timeseries.iloc[-self._maxlen:]

    def tolist(self) -> np.ndarray:
        """
        Returns a Numpy representation of TsQueue
        :return: an Numpy array
        """
        return self._timeseries.reset_index().to_numpy()

    def values(self) -> np.ndarray:
        """
        Returns values of timeseries.
        :return: an Numpy array
        """
        return self._timeseries.to_numpy().ravel()

    def timestamps(self) -> np.ndarray:
        """
        Returns timestamps of timeseries.
        :return: an Numpy array
        """
        return self._timeseries.reset_index().iloc[:,0].to_numpy().ravel()

    def earliest_value(self) -> float:
        return self._timeseries.iloc[-1,0]

    def earliest_date(self) -> int:
        return self._timeseries.reset_index().iloc[-1,0]

    def earliest_entry(self) -> np.ndarray:
        return self._timeseries.reset_index().iloc[-1]

    def size(self):
        return len(self._timeseries.index)

    def get_n_earliest_entry(self, n: int) -> np.ndarray:
        return self._timeseries.iloc[-n:].reset_index().to_numpy()