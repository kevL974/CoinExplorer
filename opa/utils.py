from typing import List, Dict
from opa.harvest.ochlv_constant import *
from opa.core.candlestick import Candlestick
from zipfile import ZipFile
from os import listdir
from os.path import join
import os


def hist_klines_websocket_to_candlestick(symbol: str, interval: str, klines: List[str]) -> Candlestick:
    """
    Convert klines to candlestick object.
    :param interval: time period of candlestick
    :param klines: OCHLV in list representation
    :return: c
    """
    return Candlestick(symbol, interval,
                       open_price=klines[IDX_OPEN],
                       close_price=klines[IDX_CLOSE],
                       high=klines[IDX_HIGHT],
                       low=klines[IDX_LOW],
                       volume=klines[IDX_VOLUME],
                       close_time=klines[IDX_CLOSE_TIME])


def stream_klines_to_candlestick(interval, klines: Dict) -> Candlestick:
    """
    Convert klines from websocket to candlestick object.
    :param interval: time period of candlestick
    :param klines: OCHLV in list representation
    :return: time period of candlestick
    """

    return Candlestick(devise=klines[KEY_SYMBOL],
                       intervalle=interval,
                       open_price=klines[KEY_OPEN],
                       close_price=klines[KEY_CLOSE],
                       high=klines[KEY_HIGHT],
                       low=klines[KEY_LOW],
                       volume=klines[KEY_VOLUME],
                       close_time=klines[KEY_CLOSE_TIME])


def list_file(directory_path: str) -> List[str]:
    """
    Returns the list of files to unzip present in the directory indicated in the variable directory_path.
    :param directory_path: Targerted directory
    :return: list of path.
    """
    files = []
    pwd = os.path.dirname(os.path.realpath(__file__))
    directory_absolut_path = os.path.join(pwd, directory_path)
    all_files_in_directory = listdir(directory_absolut_path)
    for file in all_files_in_directory:
        if file.find(".zip") >= 0:
            files.append(file)

    return files


def dezip(directory_path:  str, files: List[str]) -> None:
    """
    Uncompresses zip files in directory given in parameter
    :param directory_path: directory where zip files will be uncompressed.
    :param files: paths of zip files
    :return:
    """
    pwd = os.path.dirname(os.path.realpath(__file__))
    directory_absolut_path = os.path.join(pwd, directory_path)
    for file in files:
        file_path = join(directory_absolut_path, file)
        print(file_path)
        # ouvrir le fichier zip en mode lecture
        with ZipFile(file_path, 'r') as zip:

            # extraire tous les fichiers
            print('extraction...')
            zip.extractall(path=join(directory_absolut_path, "extract"))
            print('Terminé!')
