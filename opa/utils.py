from typing import List, Dict
from opa.harvest.ochlv_constant import *


def convert_hist_klines_websocket_to_tochlv_format(klines: List[str]) -> Dict:
    """
    Convert OCHLV in list representation to dictionnary representation.
    :param klines: OCHLV in list representation
    :return: OCHLV in dictionnary representation
    """
    tochvl = {
            KEY_CLOSE_TIME: klines[IDX_CLOSE_TIME],
            KEY_OPEN: klines[IDX_OPEN],
            KEY_CLOSE: klines[IDX_CLOSE],
            KEY_HIGHT: klines[IDX_HIGHT],
            KEY_LOW: klines[IDX_LOW],
            KEY_VOLUME: klines[IDX_VOLUME]
    }
    return tochvl
