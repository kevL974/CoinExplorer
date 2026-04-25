from typing import Dict

import numpy as np

from opa.AppException import UnavailablePriceData, UnavailableIndicatorData
from opa.core.candlestick import Candlestick
from opa.trading.indicator.base import BaseIndicator, logger
from opa.utils import TsQueue


class Environment:

    def __init__(self, price_history_size: int = 200) -> None:
        self.indicators_manager: IndicatorManager = IndicatorManager(price_history_size)
        self.price_manager: PriceManager = PriceManager(price_history_size)

    def put(self, candlestick: Candlestick) -> None:
        """
        Puts candlestick data into asset history and updates all indicators
        :param candlestick: Candlestick - A trading candlestick
        :return:
        """
        self.__update_price_movement(candlestick)

    def add_indicator(self, tunit: str, indicator: BaseIndicator) -> None:
        self.__add_indicator(tunit, indicator)

    def indicator_value(self, id_indicator: str) -> np.ndarray:
        try:
            indicator_value = self.indicators_manager.indicator_value(self.price_manager, id_indicator)
        except UnavailablePriceData as e:
            raise UnavailableIndicatorData from e
        else:
            return indicator_value

    def price_value(self, tunit: str) -> Dict[str, float]:
        return self.price_manager.earliest_price(tunit)

    def price_history(self, tunit: str) -> Dict[str, np.ndarray]:
        try:
            history = self.price_manager.history(tunit)
        except KeyError as e:
            msg = f"Unavailable price data for tunit {tunit}"
            logger.warning(msg)
            raise UnavailablePriceData(msg) from e
        else:
            return history

    def __add_indicator(self, tunit: str, indicator: BaseIndicator) -> None:
        self.indicators_manager.add(tunit, indicator)

    def __update_price_movement(self, candlestick: Candlestick) -> None:
        tunit = candlestick.interval
        ts = candlestick.close_time
        close = candlestick.close
        low = candlestick.low
        high = candlestick.high
        self.price_manager.put(tunit, ts, close, low, high)

    @staticmethod
    def create_identifier(id_tunit: str, indicator: BaseIndicator) -> str:
        return f"{id_tunit}-{indicator.__str__()}"


class PriceManager:

    def __init__(self, nb_records: int) -> None:
        self.__nb_records: int = nb_records
        self._closes: Dict[str, TsQueue] = {}
        self._highs: Dict[str, TsQueue] = {}
        self._lows: Dict[str, TsQueue] = {}

    def put(self, tunit: str, ts: int, close: float, low: float, high: float) -> None:
        if not self.exist(tunit):
            self._closes[tunit] = TsQueue(self.__nb_records)
            self._highs[tunit] = TsQueue(self.__nb_records)
            self._lows[tunit] = TsQueue(self.__nb_records)

        self._closes[tunit].push(ts, close)
        self._highs[tunit].push(ts,high)
        self._lows[tunit].push(ts,low)

    def history(self, tunit) -> Dict[str, np.ndarray]:
        if self.exist(tunit):
            prices= {
                "close": self._closes[tunit].values(),
                "high": self._highs[tunit].values(),
                "low":  self._lows[tunit].values()
            }
        else :
            msg = f"No price history for tunit = {tunit}"
            logger.warning(msg)
            raise KeyError(msg)

        return prices

    def earliest_price(self, tunit: str) -> Dict[str,float]:
        prices = {}
        if self.exist(tunit):
            prices = {
                "close": self._closes[tunit].earliest_value(),
                "highs": self._highs[tunit].earliest_value(),
                "lows": self._lows[tunit].earliest_value()
            }
        return prices


    def exist(self, tunit: str) -> bool:
        return tunit in self._closes.keys()


class IndicatorManager:

    def __init__(self, nb_records: int) -> None:
        self.__nb_records: int = nb_records
        self._indicators: Dict[str, Dict[str,Dict[str,BaseIndicator]]] = {}

    def add(self, tunit: str, indicator: BaseIndicator) -> None:
        #TODO implementer la gestion d'ajout d'indicateur en fonction de l'interval et leur id. il faut trouver une
        # structure efficace qui permet de trouver rapidement l'indicateur en fonction de l'id et l'intervalle
        # Idée 1. implementer un arbre "Composite" avec une fonction ajout 'add(indicator)'
        # la fonction prends la propriété 'id' de l'indicateur est doit etre unique. elle est doit prendre cette forme
        # tunit_nomIndicateur_param1#param2#param3
        # La fonction utilise l'id de l'indicateur pour ajouter l'indicateur à la bonne branche de l'arbre. l'id est
        # est un chemin dans l'arbre pour acceder à l'indicateur cibler
        # r  __tunit1__indicatorA__paramX
        #  \        \__indicatorB__paramX
        #   \__tunit2__indicatorA__paramY
        #

        if tunit not in self._indicators.keys():
            self._indicators[tunit] = {}

        indicator_name = indicator.get_name()

        if indicator_name not in self._indicators[tunit].keys():
            self._indicators[tunit][indicator_name] = {}

        indicator_params = indicator.get_parameters()

        if indicator_params not in self._indicators[tunit][indicator_name].keys():
            self._indicators[tunit][indicator_name][indicator_params] = indicator

    def indicator_value(self, price_manager: PriceManager, id_indicator) -> np.ndarray:
        parameters = str.split(id_indicator, "-")
        tunit = parameters[0]
        name = str.split(parameters[1], "_")[1]
        param = str.split(parameters[1], "_")[2]
        try:
            indicator = self._indicators[tunit][name][param]
        except KeyError:
            msg = f"Unavailable indicator data - id: {id_indicator} - tunit:{tunit} - name:{name} - param: {param} "
            logger.warning(msg)
            raise UnavailableIndicatorData

        try:
            tunit_price = price_manager.history(tunit)
        except KeyError as e:
            msg = f"Unavailable price data for tunit {tunit}"
            logger.warning(msg)
            raise UnavailablePriceData from e
        else:
            return indicator.value(tunit_price['high'], tunit_price['low'], tunit_price['close'])
