import json
import os
import re
import shutil
import sys
import aiohttp
import aiofiles
from aiofiles.ospath import exists as aio_exists
from aiofiles.os import makedirs as aio_makedirs
from aiofiles.os import remove as aio_remove
import urllib.request
from argparse import ArgumentTypeError
from pathlib import Path

from opa.harvest.enums import *


def get_destination_dir(file_url, folder=None):
    store_directory = os.environ.get('STORE_DIRECTORY')
    if folder:
        store_directory = folder
    if not store_directory:
        store_directory = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(store_directory, file_url)


def get_download_url(file_url):
    return "{}{}".format(BASE_URL, file_url)


def get_all_symbols(type):
    if type == 'um':
        response = urllib.request.urlopen("https://fapi.binance.com/fapi/v1/exchangeInfo").read()
    elif type == 'cm':
        response = urllib.request.urlopen("https://dapi.binance.com/dapi/v1/exchangeInfo").read()
    else:
        response = urllib.request.urlopen("https://api.binance.com/api/v3/exchangeInfo").read()
    return list(map(lambda symbol: symbol['symbol'], json.loads(response)['symbols']))


async def download_file(base_path, file_name, date_range=None, folder=None):
    download_path = "{}{}".format(base_path, file_name)
    if folder:
        base_path = os.path.join(folder, base_path)
    if date_range:
        date_range = date_range.replace(" ", "_")
        base_path = os.path.join(base_path, date_range)
    save_path = get_destination_dir(os.path.join(base_path, file_name), folder)

    if os.path.exists(save_path):
        print("\nfile already exists! {}".format(save_path))
        return save_path

    # make the directory
    if not await aio_exists(base_path):
        await aio_makedirs(Path(get_destination_dir(base_path)), exist_ok=True)

    try:
        download_url = get_download_url(download_path)

        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as dl_file:

                if dl_file.status == 200:
                    length = dl_file.headers.get('content-length')

                    length = int(length)
                    blocksize = max(4096, length // 100)

                    async with aiofiles.open(save_path, mode='wb') as out_file:
                        dl_progress = 0
                        print("\nFile Download: {}".format(save_path))

                        while True:
                            buf = await dl_file.content.read(blocksize)
                            if not buf:
                                break
                            dl_progress += len(buf)
                            await out_file.write(buf)
                            done = int(50 * dl_progress / length)
                            sys.stdout.write("\r[%s%s]" % ('#' * done, '.' * (50 - done)))
                            sys.stdout.flush()
                    return save_path

                else:
                    return None

    except aiohttp.http_exceptions.HttpProcessingError:
        print("\nFile not found: {}".format(download_url))
        aio_remove(save_path)
        return None


def convert_to_date_object(d):
    year, month, day = [int(x) for x in d.split('-')]
    date_obj = date(year, month, day)
    return date_obj


def get_start_end_date_objects(date_range):
    start, end = date_range.split()
    start_date = convert_to_date_object(start)
    end_date = convert_to_date_object(end)
    return start_date, end_date


def match_date_regex(arg_value, pat=re.compile(r'\d{4}-\d{2}-\d{2}')):
    if not pat.match(arg_value):
        raise ArgumentTypeError
    return arg_value


def check_directory(arg_value):
    if os.path.exists(arg_value):
        while True:
            option = input('Folder already exists! Do you want to overwrite it? y/n  ')
            if option != 'y' and option != 'n':
                print('Invalid Option!')
                continue
            elif option == 'y':
                shutil.rmtree(arg_value)
                break
            else:
                break
    return arg_value


def raise_arg_error(msg):
    raise ArgumentTypeError(msg)


def get_path(symbol, interval=None):
    trading_type_path = 'data/spot'
    if interval is not None:
        path = f'{trading_type_path}/monthly/klines/{symbol.upper()}/{interval}/'
    else:
        path = f'{trading_type_path}/monthly/klines/{symbol.upper()}/'
    return path
