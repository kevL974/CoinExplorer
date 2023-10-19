import argparse
import asyncio
import os
from datetime import datetime
from binance import AsyncClient
from opa.storage.connector import InputOutputStream, CsvConnector
from typing import List

API_KEY = os.getenv("API_KEY_BINANCE_TESTNET")
API_SECRET = os.getenv("API_KEY_SECRET_BINANCE_TESTNET")

def collect_hist_data(symbols: List[str], intervals: List[str], output: InputOutputStream) -> None:
    """
    Collect all historical data foreach symbols and intervals and save them in output given in parameter.
    :param symbols: List of targeted symbols e.g ["BTCUSDT", "ETHBTC"]
    :param intervals: List of candleline intervals in string format e.g ["1m", "15m"]
    :return:
    """

    # écrire les données récupérées avec cette méthode
    # output.write()
    pass


def collect_stream_data(symbols: List[str], intervals: List[str], output: InputOutputStream) -> None:
    """
    Collect data in real time foreach symbols and intervals and save them in output given in parameter.
    :param symbols: List of targeted symbols e.g ["BTCUSDT", "ETHBTC"]
    :param intervals: List of candleline intervals in string format e.g ["1m", "15m"]
    :return:
    """
    # for symbol_i in symbols:
    #     for interval_j in intervals:

    # écrire les données récupérées avec cette méthode
    # output.write()
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make some trades with Binance')
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

    symbols = args.symbol
    intervals = args.interval

    output = CsvConnector()
    collect_hist_data(symbols, intervals, output)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(collect_stream_data(symbols, intervals, output))

