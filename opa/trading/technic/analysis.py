from abc import ABC, abstractmethod
from typing import Dict
from kafka.errors import IllegalArgumentError

from opa.AppException import UnavailablePriceData, UnavailableIndicatorData
from opa.utils import TsQueue
from opa.core.candlestick import Candlestick
import talib
import numpy as np
import logging
logger = logging.getLogger(__name__)




class Indicator(ABC):

    NAME: str = "BaseIndicator"

    def __init__(self, tunit):
        super().__init__()
        self.__tunit=tunit

    @abstractmethod
    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        pass

    def get_name(self) -> str:
        return self.NAME

    def tunit(self) -> str:
        return self.__tunit

    @abstractmethod
    def get_parameters(self) -> str:
        pass

    def get_id(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"{self.tunit()}_{self.get_name()}_{self.get_parameters()}"



class SmaIndicator(Indicator):
    NAME: str = "SMA"

    def __init__(self, tunit: str, period: int) -> None:
        super().__init__(tunit)
        if period < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {period}")
        self._period = period

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.SMA(closes, timeperiod=self._period)

    def get_parameters(self) -> str:
        return str(self._period)


class RsiIndicator(Indicator):
    NAME: str = "RSI"

    def __init__(self, tunit: str,  period: int) -> None:
        if period < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {period}")
        super().__init__(tunit)
        self._period = period

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.RSI(np.array(closes), timeperiod=self._period)

    def get_parameters(self) -> str:
        return str(self._period)

class StochasticIndicator(Indicator):
    NAME: str = "Stochastic"

    def __init__(self,
                 tunit: str,
                 fastk_period: int = 12,
                 slowk_period: int = 3,
                 slowk_matype: int = 0,
                 slowd_period: int = 3,
                 slowd_matype: int = 0) -> None:

        if fastk_period < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {fastk_period}")
        if slowk_period < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {slowk_period}")
        if slowk_matype < 0:
            raise IllegalArgumentError(f"Period must be positive integer: {slowk_matype}")
        if slowd_period < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {slowd_period}")
        if slowd_matype < 0:
            raise IllegalArgumentError(f"Period must be positive integer: {slowd_matype}")

        super().__init__(tunit)
        self._fastk_period = fastk_period
        self._slowk_period = slowk_period
        self._slowk_matype = slowk_matype
        self._slowd_period = slowd_period
        self._slowd_matype = slowd_matype

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.STOCH(highs,
                            closes,
                            lows,
                            self._fastk_period,
                            self._slowk_period,
                            self._slowk_matype,
                            self._slowd_period,
                            self._slowd_matype)

    def get_parameters(self) -> str:
        return f"{str(self._fastk_period)}#{str(self._slowk_period)}#{str(self._slowd_period)}"


class MACDIndicator(Indicator):
    NAME: str = "MACD"

    def __init__(self,
                 tunit: str,
                 fastperiod: int = 12,
                 slowperiod: int = 26,
                 signalperiod: int = 9) -> None:
        if fastperiod < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {fastperiod}")
        if slowperiod < 1 :
            raise IllegalArgumentError(f"Period must be positive integer: {slowperiod}")
        if signalperiod < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {signalperiod}")

        super().__init__(tunit)
        self._fastperiod: int = fastperiod
        self._slowperiod: int = slowperiod
        self._signalperiod: int = signalperiod

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.MACD(closes, self._fastperiod, self._slowperiod, self._signalperiod)

    def get_parameters(self) -> str:
        return f"{str(self._fastperiod)}#{str(self._slowperiod)}#{str(self._signalperiod)}"


class ParabolicSARIndicator(Indicator):
    NAME: str = "SAR"

    def __init__(self,tunit: str, acceleration: float, maximum: float) -> None:
        super().__init__(tunit)
        if (acceleration < 0) or (maximum < 0):
            raise ValueError()

        self._acceleration: float = acceleration
        self._maximum: float = maximum

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.SAR(highs, lows, acceleration=0.02, maximum=0.2)

    def get_parameters(self) -> str:
        return f"{str(self._acceleration)}#{str(self._maximum)}"


class Environment:
    __MAXSIZE: int = 200

    def __init__(self):
        self.indicators_manager: IndicatorManager = IndicatorManager(Environment.__MAXSIZE)
        self.price_manager: PriceManager = PriceManager(Environment.__MAXSIZE)

    def put(self, candlestick: Candlestick) -> None:
        """
        Puts candlestick data into asset history and updates all indicators
        :param candlestick: Candlestick - A trading candlestick
        :return:
        """
        self.__update_price_movement(candlestick)

    def add_indicator(self, tunit: str, indicator: Indicator) -> None:
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

    def __add_indicator(self, tunit: str, indicator: Indicator) -> None:
        self.indicators_manager.add(tunit, indicator)

    def __update_price_movement(self, candlestick: Candlestick) -> None:
        tunit = candlestick.interval
        ts = candlestick.close_time
        close = candlestick.close
        low = candlestick.low
        high = candlestick.high
        self.price_manager.put(tunit, ts, close, low, high)

    @staticmethod
    def create_identifier(id_tunit: str, indicator: Indicator) -> str:
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
        self._indicators: Dict[str, Dict[str,Dict[str,Indicator]]] = {}

    def add(self, tunit: str, indicator: Indicator) -> None:
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
        except KeyError as e0:
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