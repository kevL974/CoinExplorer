import argparse
import asyncio
import os
from binance import AsyncClient, BinanceSocketManager
from opa.storage.connector import InputOutputStream, KafkaConnector
from opa.utils import *
from opa.util.binance.enums import *
from typing import List

API_KEY = os.getenv("API_KEY_BINANCE_TESTNET")
API_SECRET = os.getenv("API_KEY_SECRET_BINANCE_TESTNET")


async def get_missing_data(client: AsyncClient, symbol: str, interval: str, output: InputOutputStream,
                           lock: asyncio.Lock) -> None:
    """
    Get earliest data from websocket stream.
    :param lock: a asyncio.Lock object
    :param client: Binance AsyncClient from Binance API
    :param symbol: Targeted symbol.
    :param interval: Targeted interval.
    :param output: Place where data will be saved.
    :return:
    """
    klines = await client.get_historical_klines(symbol, interval, "1 years ago UTC")
    candlesticks = []
    for kline in klines:
        candlesticks.append(hist_klines_websocket_to_candlestick(symbol, interval, kline))

    async with lock:
        output.write_lines(candlesticks, topic=candlesticks[0].symbol)


async def start_collecting(client: AsyncClient, symbol: str, interval: str, output: InputOutputStream,
                           lock: asyncio.Lock) -> None:
    """
    Get latest data from websocket stream.
    :param lock: a asyncio.Lock object
    :param client: Binance AsyncClient from Binance API
    :param symbol: Targeted symbol.
    :param interval: Targeted interval.
    :param output: Place where data will be saved.
    :return:
    """

    bm = BinanceSocketManager(client)
    ks = bm.kline_socket(symbol, interval)
    async with ks as kscm:
        while True:
            kline_socket_msg = await kscm.recv()
            kline = kline_socket_msg[KEY_KLINE_CONTENT]
            if kline[KEY_FINAL_BAR]:
                candlestick = stream_klines_to_candlestick(interval, kline)
                async with lock:
                    output.write(candlestick, topic=candlestick.symbol)


async def start_stream_data_collector(client: AsyncClient, symbol: str, interval: str, output: InputOutputStream, lock: asyncio.Lock) -> None:
    """
    Updates missing data from historical data and collect data from Binance web socket for symbol and interval given
    in parameter and saves them in output.
    :param lock: a asyncio.Lock object
    :param client: Binance AsyncClient from Binance API
    :param symbol: Targeted symbol.
    :param interval: Targeted interval.
    :param output: Place where data will be saved.
    :return:
    """
    await get_missing_data(client, symbol, interval, output, lock)
    await start_collecting(client, symbol, interval, output, lock)


async def collect_stream_data(symbols: List[str], intervals: List[str], output: InputOutputStream) -> None:
    """
    Collects data in real time foreach symbols and intervals and save them in output given in parameter.
    :param symbols: List of targeted symbols e.g ["BTCUSDT", "ETHBTC"]
    :param intervals: List of candleline intervals in string format e.g ["1m", "15m"]
    :return:
    """
    client = await AsyncClient.create(api_key=API_KEY, api_secret=API_SECRET, testnet=True)
    collectors = []

    lock = asyncio.Lock()
    for symbol_i in symbols:
        for interval_j in intervals:
            collectors.append(asyncio.ensure_future(start_stream_data_collector(client,
                                                                                symbol_i,
                                                                                interval_j,
                                                                                output,
                                                                                lock)))

    finished, _ = await asyncio.wait(collectors)
    client.close_connection()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make some trades with Binance')
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
    parser.add_argument('-k', '--kafka',
                        help='kafka connection setting : -k <ip_boostrapserver>:<port_bootstrapserver>',
                        type=str,
                        required=True)
    parser.add_argument('--skip_stream_data', help='Skip streaming data gathering', action='store_true')
    parser.add_argument('--debug', help='activate debug mode', action='store_true')
    args = parser.parse_args()

    symbols = args.symbol
    intervals = args.interval
    kafka_host, kafka_port = parse_connection_settings(args.kafka)
    output_kafka = KafkaConnector(bootstrapservers=args.kafka, clientid="opa_producer")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(collect_stream_data(symbols, intervals, output_kafka))

