import argparse
from opa.storage.connector import InputOutputStream, HbaseTableConnector,
from opa.utils import *
from opa.harvest.enums import *
from typing import List
from opa.harvest.download_kline import download_monthly_klines
from tqdm import tqdm


def collect_hist_data(symbols: List[str], intervals: List[str], output: InputOutputStream) -> None:
    """
    Collect all historical data for each symbols and intervals and save them in output given in parameter.
    :param symbols: List of targeted symbols e.g ["BTCUSDT", "ETHBTC"]
    :param intervals: List of candleline intervals in string format e.g ["1m", "15m"]
    :return:
    """
    paths = download_monthly_klines(symbols, intervals)

    for symbol, interval, path in paths:
        list_files_csv = dezip(path)
        for csv_files in tqdm(list_files_csv):
            list_hbase = csv_to_candlesticks(symbol, interval, csv_files)
            output.write_lines(list_hbase, batch_size=500)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Collect historic candlesticks data from Binance.')
    parser.add_argument('-s', '--symbol',
                        help='Symbol that will be extracted in string format. ex :\'BTCUSDT\'',
                        nargs='+',
                        type=str,
                        choices=['BTCUSDT', 'ETHBTC', 'ETHUSDT'],
                        required=True)
    parser.add_argument('-i', '--interval',
                        help='Symbol that will be extracted',
                        nargs='+',
                        type=str,
                        choices=INTERVALS,
                        required=True)
    parser.add_argument('-d', '--database',
                        help='database connection setting : -d <ip_database>:<port_database>',
                        type=str,
                        required=True)
    parser.add_argument('--skip_hist_data', help='Skip historic data downloading', action='store_true')
    parser.add_argument('--debug', help='activate debug mode', action='store_true')
    args = parser.parse_args()

    symbols = args.symbol
    intervals = args.interval
    db_host, db_port = parse_connection_settings(args.database)

    output_hbase = HbaseTableConnector(host=db_host, port=db_port, table_name='BINANCE')

    collect_hist_data(symbols, intervals, output_hbase)


