#!/usr/bin/env python

import sys
from datetime import *
import pandas as pd
from enums import *
from utility import download_file, get_all_symbols, get_parser, get_start_end_date_objects, convert_to_date_object, \
    get_path
from zipfile import ZipFile
from os import listdir
from os.path import isfile, join


def download_monthly_klines(trading_type, symbols, intervals, years=YEARS, months=MONTHS, start_date="", end_date="",
                            folder="", checksum=""):
    current = 0
    date_range = None

    parser = get_parser('klines')
    args = parser.parse_args(sys.argv[1:])
    print("Voici les arguments", args)

    trading_type = "spot"
    num_symbols = len(symbols)

    period = convert_to_date_object(datetime.today().strftime('%Y-%m-%d')) - convert_to_date_object(
        PERIOD_START_DATE)
    dates = pd.date_range(end=datetime.today(), periods=period.days + 1).to_pydatetime().tolist()
    dates = [date.strftime("%Y-%m-%d") for date in dates]

    if start_date and end_date:
        date_range = start_date + " " + end_date

    if not start_date:
        start_date = START_DATE
    else:
        start_date = convert_to_date_object(start_date)

    if not end_date:
        end_date = END_DATE
    else:
        end_date = convert_to_date_object(end_date)

    print("Found {} symbols".format(num_symbols))

    for symbol in symbols:
        print("[{}/{}] - start download monthly {} klines ".format(current + 1, num_symbols, symbol))
        for interval in intervals:
            for year in years:
                for month in months:
                    current_date = convert_to_date_object('{}-{}-01'.format(year, month))
                    print(current_date
                          )
                    if start_date <= current_date <= end_date:
                        path = get_path(trading_type, "klines", "monthly", symbol, interval)
                        print(path)
                        chemin = join(trading_type, "klines", "monthly", symbol, interval)
                        file_name = "{}-{}-{}-{}.zip".format(symbol.upper(), interval, year, '{:02d}'.format(month))

                        download_file(path, file_name, date_range, folder)

                        if checksum == 1:
                            checksum_path = get_path(trading_type, "klines", "monthly", symbol, interval)
                            checksum_file_name = "{}-{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, year,
                                                                                   '{:02d}'.format(month))
                            download_file(checksum_path, checksum_file_name, date_range, folder)

        current += 1
    return path
