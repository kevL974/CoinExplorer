from enums import *
from utility import download_file, convert_to_date_object, get_path
import os

def download_monthly_klines(symbols, intervals, folder="", checksum=""):
    current = 0
    num_symbols = len(symbols)

    print("Found {} symbols".format(num_symbols))
    pwd = os.path.dirname(os.path.realpath(__file__))
    for symbol in symbols:
        print("[{}/{}] - start download monthly {} klines ".format(current + 1, num_symbols, symbol))
        for interval in intervals:
            for year in YEARS:
                for month in MONTHS:
                    current_date = convert_to_date_object('{}-{}-01'.format(year, month))
                    print(current_date)
                    if START_DATE <= current_date <= END_DATE:
                        path = get_path(symbol, interval)
                        paths = os.path.join(pwd, path)
                        file_name = "{}-{}-{}-{}.zip".format(symbol.upper(), interval, year, '{:02d}'.format(month))

                        download_file(path, file_name, folder)

                        if checksum == 1:
                            checksum_path = get_path(symbol, interval)
                            checksum_file_name = "{}-{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, year,
                                                                                   '{:02d}'.format(month))
                            download_file(checksum_path, checksum_file_name, folder)

        current += 1
    print("Voici le path de download",paths)
    return paths
