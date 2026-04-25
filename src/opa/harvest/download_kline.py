import logging
from opa.util.binance.enums import *
from opa.harvest.utility import download_file, convert_to_date_object, get_path
import os

logger = logging.getLogger(__name__)

def download_monthly_klines(symbols, intervals, folder="", checksum=""):
    current = 0
    num_symbols = len(symbols)
    list_paths = []
    logger.info("Found %d symbols", num_symbols)
    pwd = os.path.dirname(os.path.realpath(__file__))
    for symbol in symbols:
        logger.info("[%d/%d] - start download monthly %s klines", current + 1, num_symbols, symbol)
        for interval in intervals:
            for year in YEARS:
                for month in MONTHS:
                    current_date = convert_to_date_object('{}-{}-01'.format(year, month))
                    logger.debug("current_date: %s", current_date)
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
            list_paths.append((symbol,  interval, paths))

        current += 1
    return list_paths
