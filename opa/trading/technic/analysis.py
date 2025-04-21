from abc import ABC, abstractmethod
from typing import Dict, List

from kafka.errors import IllegalArgumentError
import talib
from opa.utils import TsQueue
from opa.core.candlestick import Candlestick
from opa.util.binance.enums import *
import numpy as np


class Indicator(ABC):

    NAME: str = "BaseIndicator"

    def __init__(self):
        super().__init__()

    @abstractmethod
    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        pass

    def get_name(self) -> str:
        return self.NAME

    @abstractmethod
    def get_parameters(self) -> str:
        pass

    def get_id(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"{self.get_name()}_{self.get_parameters()}"



class SmaIndicator(Indicator):
    NAME: str = "SMA"

    def __init__(self, period: int) -> None:
        super().__init__()
        if period < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {period}")
        self._period = period

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.SMA(closes, timeperiod=self._period)

    def get_parameters(self) -> str:
        return str(self._period)


class RsiIndicator(Indicator):
    NAME: str = "RSI"

    def __init__(self, period: int) -> None:
        if period < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {period}")
        super().__init__()
        self._period = period

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.RSI(np.array(closes), timeperiod=self._period)

    def get_parameters(self) -> str:
        return str(self._period)

class StochasticIndicator(Indicator):
    NAME: str = "Stochastic"

    def __init__(self,
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

        super().__init__()
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
                 fastperiod: int = 12,
                 slowperiod: int = 26,
                 signalperiod: int = 9) -> None:
        if fastperiod < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {fastperiod}")
        if slowperiod < 1 :
            raise IllegalArgumentError(f"Period must be positive integer: {slowperiod}")
        if signalperiod < 1:
            raise IllegalArgumentError(f"Period must be positive integer: {signalperiod}")

        super().__init__()
        self._fastperiod: int = fastperiod
        self._slowperiod: int = slowperiod
        self._signalperiod: int = signalperiod

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.MACD(closes, self._fastperiod, self._slowperiod, self._signalperiod)

    def get_parameters(self) -> str:
        return f"{str(self._fastperiod)}#{str(self._slowperiod)}#{str(self._signalperiod)}"


class ParabolicSARIndicator(Indicator):
    NAME: str = "SAR"

    def __init__(self, acceleration: float, maximum: float) -> None:
        super().__init__()
        if (acceleration < 0) or (maximum < 0):
            raise ValueError()

        self._acceleration: float = acceleration
        self._maximum: float = maximum

    def value(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
        return talib.SAR(highs, lows, acceleration=0.02, maximum=0.2)

    def get_parameters(self) -> str:
        return f"{str(self._acceleration)}#{str(self._maximum)}"


class IndicatorSet:
    __MAXSIZE: int = 200

    def __init__(self):
        self._indicators: Dict[str, Dict[str, Indicator]] = {}
        self._indicator_ts: Dict[str, np.ndarray] = {}
        self._closes: Dict[str, TsQueue] = {}
        self._highs: Dict[str, TsQueue] = {}
        self._lows: Dict[str, TsQueue] = {}
        self.__configure_queues()
        self._authorized_tunit=[]

    def add(self, tunit, indicator: Indicator):
        self.__add_tunit_filter(tunit)
        self.__add_price_history(tunit)
        self.__add_indicator(tunit, indicator)

    def __configure_queues(self) -> None:
        pass

    def __add_tunit_filter(self, tunit: str) -> None:
        if tunit not in INTERVALS:
            raise IllegalArgumentError(f"Time unit {tunit} is not permitted")

        self._authorized_tunit.append(tunit)

    def __add_price_history(self, tunit: str) -> None:
        if tunit not in self._closes.keys():
            self._closes[tunit] = TsQueue(maxlen=Environment.__MAXSIZE)

        if tunit not in self._lows.keys():
            self._lows[tunit] = TsQueue(maxlen=Environment.__MAXSIZE)

        if tunit not in self._highs.keys():
            self._highs[tunit] = TsQueue(maxlen=Environment.__MAXSIZE)

    def __add_indicator(self, tunit: str, indicator: Indicator) -> None:
        indicator_id = self.create_id(tunit, indicator)

        if tunit not in self._indicators.keys():
            self._indicators[tunit] = {}

        if not self.indicator_exist(indicator_id):
            self._indicators[tunit][indicator_id] = indicator
            self._indicator_ts[indicator_id] = np.array([np.nan] for x in range(0, Environment.__MAXSIZE, 1))

    def __update_indicators(self, tunit: str) -> None:
        np_highs = self._highs[tunit].values()
        np_lows = self._lows[tunit].values()
        np_closes = self._closes[tunit].values()

        for id, indicator in self._indicators[tunit].items():
            self._indicator_ts[id] = indicator.value(np_highs, np_lows, np_closes)

    def get_indicator_history(self, indicator_id: str) -> np.ndarray:
        if not self.indicator_exist(indicator_id):
            raise KeyError(f"Indicator {indicator_id} does not exist")

        return self._indicator_ts[indicator_id]


    def get_indicator_value(self, indicator_id: str) -> float:
        indicator_history = self.get_indicator_history(indicator_id)

        return indicator_history[-1]

    def get_close_value(self,):

    def indicator_exist(self, indicator_id: str) -> bool:
        for tunit, indicators in self._indicators.items():
            if indicator_id in indicators.keys():
                return True

        return False

    def is_authorized(self, tunit: str) -> bool:
        return tunit in self._authorized_tunit

    def receive_new_candlestick(self, candlestick: Candlestick) -> None:
        tunit = candlestick.interval
        ts = candlestick.close_time
        close = candlestick.close
        low = candlestick.low
        high = candlestick.high

        if self.is_authorized(tunit):
            self._closes[tunit].append(ts,close)
            self._lows[tunit].append(ts, low)
            self._highs[tunit].append(ts, high)
            self.__update_indicators(tunit)

    @staticmethod
    def create_id(tunit: str, indicator: Indicator) -> str:
        return f"{tunit}-{indicator.__str__()}"

    @staticmethod
    def get_tunit_from_id(id_indicator: str) -> str:
        return str.split(id_indicator,"-")[0]

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
        self.__update_indicators()

    def add_indicator(self, tunit: str, indicator: Indicator) -> None:
        self.__add_indicator(tunit, indicator)

    def current_value(self, id_indicator) -> float:
        pass

    def history(self,id_indicator) -> np.ndarray:
        pass

    def __add_indicator(self, tunit: str, indicator: Indicator) -> None:
        self.indicators_manager.add(tunit, indicator)

    def __update_price_movement(self, candlestick: Candlestick) -> None:
        tunit = candlestick.interval
        ts = candlestick.close_time
        close = candlestick.close
        low = candlestick.low
        high = candlestick.high
        self.price_manager.put(tunit, ts, close, low, high)

    def __update_indicators(self, candlestick: Candlestick) -> None:
        tunit = candlestick.interval

        self.indicators_manager.update(self.price_manager)

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
            self.lows[tunit] = TsQueue(self.__nb_records)

        self._closes[tunit].append(ts, close)
        self._highs[tunit].append(ts,high)
        self._lows[tunit].append(ts,low)

    def get_prices(self, tunit) -> Dict[str, np.ndarray]:
        if self.exist(tunit):
            prices= {
                "close": self._closes[tunit].tolist(),
                "highs": self._highs[tunit].tolist(),
                "lows":  self._lows[tunit].tolist()
            }
        else :

        return prices


    def exist(self, tunit: str) -> bool:
        return tunit in self._closes.keys()

class IndicatorManager:

    def __init__(self, nb_records: int) -> None:
        self.__nb_records: int = nb_records
        self._indicators: Dict[str, Dict[str,Dict[str,Indicator]]]

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

