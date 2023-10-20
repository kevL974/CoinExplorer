from typing import List, Dict
from opa.harvest.ochlv_constant import *


def convert_hist_klines_websocket_to_stochlv_format(symbol: str, klines: List[str]) -> Dict:
    """
    Convert OCHLV in list representation to dictionnary representation.
    :param klines: OCHLV in list representation
    :return: OCHLV in dictionnary representation
    """
    tochvl = {
            KEY_SYMBOL: symbol,
            KEY_CLOSE_TIME: klines[IDX_CLOSE_TIME],
            KEY_OPEN: klines[IDX_OPEN],
            KEY_CLOSE: klines[IDX_CLOSE],
            KEY_HIGHT: klines[IDX_HIGHT],
            KEY_LOW: klines[IDX_LOW],
            KEY_VOLUME: klines[IDX_VOLUME]
    }
    return tochvl


def convert_stream_klines_to_stochlv_format(klines: Dict) -> Dict:
    """
    Convert OCHLV in dictionnary representation from websocket to dictionnary representation.
    :param klines: OCHLV in list representation
    :return: OCHLV in dictionnary representation
    """
    tochvl = {
        KEY_SYMBOL: klines[KEY_SYMBOL],
        KEY_CLOSE_TIME: klines[KEY_CLOSE_TIME],
        KEY_OPEN: klines[KEY_OPEN],
        KEY_CLOSE: klines[KEY_CLOSE],
        KEY_HIGHT: klines[KEY_HIGHT],
        KEY_LOW: klines[KEY_LOW],
        KEY_VOLUME: klines[KEY_VOLUME]
    }

    return tochvl
