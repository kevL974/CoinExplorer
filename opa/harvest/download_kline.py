from enums import *
from utility import download_file, convert_to_date_object, get_path


def download_monthly_klines(symbols, intervals, folder="", checksum=""):
    current = 0
    num_symbols = len(symbols)

    print("Found {} symbols".format(num_symbols))

    for symbol in symbols:
        print("[{}/{}] - start download monthly {} klines ".format(current + 1, num_symbols, symbol))
        for interval in intervals:
            for year in YEARS:
                for month in MONTHS:
                    current_date = convert_to_date_object('{}-{}-01'.format(year, month))
                    print(current_date)
                    if START_DATE <= current_date <= END_DATE:
                        path = get_path(symbol, interval)
                        print(path)
                        file_name = "{}-{}-{}-{}.zip".format(symbol.upper(), interval, year, '{:02d}'.format(month))

                        download_file(path, file_name, folder)

                        if checksum == 1:
                            checksum_path = get_path(symbol, interval)
                            checksum_file_name = "{}-{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, year,
                                                                                   '{:02d}'.format(month))
                            download_file(checksum_path, checksum_file_name, folder)

        current += 1
    return path
