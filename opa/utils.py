from typing import List, Dict
from opa.harvest.ochlv_constant import *
from opa.core.candlestick import Candlestick
from zipfile import ZipFile
from os import listdir
from os.path import join
import os
import csv


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

    return Candlestick(symbol=klines[KEY_SYMBOL],
                       interval=interval,
                       open_price=klines[KEY_OPEN],
                       close_price=klines[KEY_CLOSE],
                       high=klines[KEY_HIGHT],
                       low=klines[KEY_LOW],
                       volume=klines[KEY_VOLUME],
                       close_time=klines[KEY_CLOSE_TIME])


def csv_to_candlesticks(symbol: str,  interval: str, csv_filepath: str) -> List[Candlestick]:
    """
    Read csv file that contents candlesticks and  transforms them to list Candlestick object.
    :param symbol: symbol of candlestick in csv file
    :param interval: interval of candlestick in csv file
    :param csv_filepath: path to csv file
    :return: a list of Candlestick object
    """
    candlesticks = []
    with open(csv_filepath, newline='\n') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            candlesticks.append(Candlestick(symbol=symbol,
                                            interval=interval,
                                            open_price=float(row[1]),
                                            high=float(row[2]),
                                            low=float(row[3]),
                                            close_price=float(row[4]),
                                            volume=float(row[5]),
                                            close_time=int(row[6])))
    return candlesticks


def list_file(directory_path: str,extension: str) -> List[str]:
    """
    Returns the list of files to unzip present in the directory indicated in the variable directory_path.
    :param directory_path: Targerted directory
    :return: list of path.
    """
    files = []
    all_files_in_directory = listdir(directory_path)
    print(all_files_in_directory)
    for file in all_files_in_directory:
        if (file.find(extension) >= 0) & (os.path.isdir(file) == False):
            files.append(file)
        else:
            print("file à ne pas dezipper:", file)

    print(files)
    return files


def dezip(directory_path:  str) -> List[str]:
    """
    Uncompresses zip files in directory given in parameter
    :param directory_path: directory where zip files will be uncompressed.
    :param files: paths of zip files
    :return:
    """
    list_files_csv = []
    list_files = list_file(directory_path, ".zip")
    print(list_files)
    pwd = os.path.dirname(os.path.realpath(__file__))
    directory_absolut_path = os.path.join(pwd, directory_path)
    i = 0

    for i in range(len(list_files)):
        file_path = join(directory_absolut_path, list_files[i])
        print(file_path)
        # ouvrir le fichier zip en mode lecture
        with ZipFile(file_path, 'r') as zip:
            # extraire tous les fichiers
            print('extraction...')
            zip.extractall(path=join(directory_absolut_path, "extract"))
            print('Terminé!')
        list_files_csv.append(os.path.join(directory_absolut_path, "extract", list_files[i].replace('zip', 'csv')))

    return list_files_csv

         