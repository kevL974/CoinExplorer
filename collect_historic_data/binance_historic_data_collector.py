import argparse
import asyncio
from opa.storage.connector import InputOutputStream, HbaseTableConnector
from opa.utils import *
from opa.harvest.enums import *
from typing import List
from opa.harvest.utility import download_file, convert_to_date_object, get_path
from tqdm.asyncio import tqdm

BATCH_SIZE = 10000


async def start_historic_data_collector(symbol: str, interval: str, year: str, month: int, output: InputOutputStream,
                                        lock: asyncio.Lock) -> None:
    """
    Collects historical data for one given parameters and save them to database.
    :param symbol: Targeted symbol.
    :param interval: Targeted  interval.
    :param year: year in string format.
    :param month: integer between 1-12.
    :param output: Place where data will be saved.
    :param lock: a asyncio.Lock object.
    :return:
    """
    current_date = convert_to_date_object('{}-{}-01'.format(year, month))
    if START_DATE <= current_date <= END_DATE:
        path = get_path(symbol, interval)
        file_name = "{}-{}-{}-{}.zip".format(symbol.upper(), interval, year, '{:02d}'.format(month))

        dl_path = await download_file(path, file_name, folder="")

        if dl_path is not None:
            csv_file = await dezip(dl_path)
            list_hbase = await csv_to_candlesticks(symbol, interval, csv_file)
            async with lock:
                output.write_lines(list_hbase, batch_size=BATCH_SIZE)


async def collect_hist_data(symbols: List[str], intervals: List[str], output: InputOutputStream) -> None:
    """
    Collect all historical data for each symbols and intervals and save them in output given in parameter.
    :param symbols: List of targeted symbols e.g ["BTCUSDT", "ETHBTC"]
    :param intervals: List of candleline intervals in string format e.g ["1m", "15m"]
    :return:
    """
    collectors = []
    lock = asyncio.Lock()
    current = 1
    num_symbols = len(symbols)
    print("Found {} symbols".format(num_symbols))
    for symbol in symbols:
        print("[{}/{}] - start download monthly {} klines ".format(current, num_symbols, symbol))
        for interval in intervals:
            for year in YEARS:
                for month in MONTHS:
                    collectors.append(asyncio.ensure_future(start_historic_data_collector(symbol,
                                                                                          interval,
                                                                                          year,
                                                                                          month,
                                                                                          output,
                                                                                          lock)))
        current += 1

    for f in tqdm(asyncio.as_completed(collectors), total=len(collectors)):
        await f
    #finished, _ = await tqdm(collectors)

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

    loop = asyncio.get_event_loop()
    loop.run_until_complete(collect_hist_data(symbols, intervals, output_hbase))
