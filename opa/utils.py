from typing import List, Dict
from opa.harvest.ochlv_constant import *
from zipfile import ZipFile
from os import listdir
from os.path import join
import os


def convert_hist_klines_websocket_to_stochlv_format(symbol: str, klines: List[str]) -> Dict:
    """
    Convert OCHLV in list representation to dictionnary representation.
    :param klines: OCHLV in list representation
    :return: OCHLV in dictionnary representation
    """
    tochvl = {
            KEY_SYMBOL: symbol,
            KEY_CLOSE_TIME: klines[IDX_CLOSE_TIME],
            KEY_OPEN: klines[IDX_OPEN],
            KEY_CLOSE: klines[IDX_CLOSE],
            KEY_HIGHT: klines[IDX_HIGHT],
            KEY_LOW: klines[IDX_LOW],
            KEY_VOLUME: klines[IDX_VOLUME]
    }
    return tochvl


def convert_stream_klines_to_stochlv_format(klines: Dict) -> Dict:
    """
    Convert OCHLV in dictionnary representation from websocket to dictionnary representation.
    :param klines: OCHLV in list representation
    :return: OCHLV in dictionnary representation
    """
    tochvl = {
        KEY_SYMBOL: klines[KEY_SYMBOL],
        KEY_CLOSE_TIME: klines[KEY_CLOSE_TIME],
        KEY_OPEN: klines[KEY_OPEN],
        KEY_CLOSE: klines[KEY_CLOSE],
        KEY_HIGHT: klines[KEY_HIGHT],
        KEY_LOW: klines[KEY_LOW],
        KEY_VOLUME: klines[KEY_VOLUME]
    }

    return tochvl


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
