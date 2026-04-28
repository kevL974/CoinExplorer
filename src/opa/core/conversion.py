"""Conversion utilities between raw Binance kline formats and Candlestick objects."""
import logging
from os.path import basename, dirname, join, realpath
from typing import Dict, List
from zipfile import BadZipfile

import aiocsv
from aiofiles import open as aio_open
from aiofiles.os import listdir
from aiofiles.ospath import isdir
from async_unzip.unzipper import unzip

from opa.core.candlestick import Candlestick
from opa.harvest.ochlv_constant import (
    IDX_CLOSE,
    IDX_CLOSE_TIME,
    IDX_HIGH,
    IDX_LOW,
    IDX_OPEN,
    IDX_VOLUME,
    KEY_CLOSE,
    KEY_CLOSE_TIME,
    KEY_HIGH,
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
                       high=float(klines[IDX_HIGH]),
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
                       high=klines[KEY_HIGH],
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
    Returns the list of files matching the given extension in the target directory.
    :param directory_path: path to the directory to scan.
    :param extension: file extension filter (e.g. ".csv", ".zip").
    :return: list of matching file names.
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
    Uncompresses a zip file and returns the path to the extracted CSV file.
    :param zip_path: relative path to the zip file to decompress.
    :return: absolute path to the extracted CSV file.
    """
    pwd = dirname(realpath(__file__))
    zip_absolut_path = join(pwd, zip_path)
    try:
        await unzip(zip_absolut_path, join(dirname(zip_absolut_path), "extract"))
    except BadZipfile as e:
        logger.error("%s : %s", e, zip_absolut_path)

    return join(dirname(zip_absolut_path), "extract", basename(zip_path).replace('zip', 'csv'))
