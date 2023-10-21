import argparse
import pandas as pd
import sys

from opa.storage.connector import InputOutputStream, CsvConnector
from typing import List
from opa.harvest.download_kline import download_monthly_klines

from datetime import *
from enums import *
from opa.harvest.utility import download_file, get_all_symbols, get_parser, get_start_end_date_objects, convert_to_date_object, \
  get_path




def collect_hist_data(market_type: List[str],symbols: List[str], intervals: List[str], output: InputOutputStream) -> None:
    """
    Collect all historical data for each symbols and intervals and save them in output given in parameter.
    :param market_type : **spot**, **um** (USD-M Futures), **cm** (COIN-M Futures)  
    :param symbols: List of targeted symbols e.g ["BTCUSDT", "ETHBTC"]
    :param intervals: List of candleline intervals in string format e.g ["1m", "15m"]
    :return:
    """


    # écrire les données récupérées avec cette méthode
    # output.write()
    download_monthly_klines(market_type,symbols,intervals)


def collect_stream_data(symbols: List[str], intervals: List[str], output: InputOutputStream) -> None:
    """
    Collect data in real time foreach symbols and intervals and save them in output given in parameter.
    :param symbols: List of targeted symbols e.g ["BTCUSDT", "ETHBTC"]
    :param intervals: List of candleline intervals in string format e.g ["1m", "15m"]
    :return:
    """

    # écrire les données récupérées avec cette méthode
    # output.write()
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make some trades with Binance')
    parser.add_argument('-t', '--type',
                        help='choice type of trading will be extract',
                        nargs='+',
                        type=str,
                        choices=['spot', 'um', 'cm'],
                        required=True)
    parser.add_argument('-s', '--symbol',
                        help='Symbol that will be extracted in string format. ex :\'BTCUSDT\'',
                        nargs='+',
                        type=str,
                        choices=['BTCUSDT', 'ETHBTC'],
                        required=True)
    parser.add_argument('-i', '--interval',
                        help='Symbol that will be extracted',
                        nargs='+',
                        type=str,
                        choices=['1m', '15m', '1d', '1M'],
                        required=True)
    parser.add_argument('--testnet', help='use binance testnet platform', action='store_true')
    parser.add_argument('--debug', help='activate debug mode', action='store_true')
    args = parser.parse_args()

    market_type = args.type
    symbols = args.symbol
    intervals = args.interval

    output = CsvConnector()
    collect_hist_data(cm,BTCUSDT,1,toto)
    collect_stream_data(market_type,symbols, intervals, output)
