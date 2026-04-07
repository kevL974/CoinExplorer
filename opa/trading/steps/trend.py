from __future__ import annotations

from opa.AppException import UnavailableData, StepError
from opa.trading.steps.base import BaseTradingStep, logger
from opa.utils import detect_convergence


class CheckBullRunStep(BaseTradingStep):

    MAX_RETRIES : int = 1400

    def __init__(self, id_sma_short: str, id_sma_long: str, id_rsi: str) -> None:
        super().__init__()
        self._id_sma_short: str = id_sma_short
        self._id_sma_long: str = id_sma_long
        self._id_rsi: str = id_rsi
        self.__nb_retries: int = 0

    def check_condition(self) -> None:
        try:
            sma_short = self.context.indicator_value(self._id_sma_short)
            sma_long = self.context.indicator_value(self._id_sma_long)
            rsi = self.context.indicator_value(self._id_rsi)
        except UnavailableData as e:
            logger.warning(e.__str__() + f" retries {self.__nb_retries}")
            if self.__nb_retries < self.MAX_RETRIES:
                self.__nb_retries += 1
                self.on_wait()
            else:
                msg = f"Can not checking condition cause indicators have issue."
                logger.error(msg)
                raise StepError(msg) from e
        else:
            self.__nb_retries = 0
            if(sma_short.ndim > 0) and (len(sma_short) > 0):
                if (sma_short[-1] > sma_long[-1]) and (rsi[-1] > 50.0).all:
                    print(f"Check bull run : sma_short ({sma_short[-1]}) > sma_long ({sma_long[-1]} and rsi ({rsi[-1]})")
                    self.on_success()
                else:
                    #print(f"Check bull run : sma_short ({sma_short[-1]}) < sma_long ({sma_long[-1]} and rsi ({rsi[-1]})")
                    self.on_fail()

    def on_fail(self) -> None:
        self.context.first_step()

    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def on_wait(self) -> None:
        pass


class ConvergingMovingAverages(BaseTradingStep):

    def __init__(self, id_sma_below: str, id_sma_above: str):
        super().__init__()
        self._id_sma_below : str = id_sma_below
        self._id_sma_above : str = id_sma_above

    def check_condition(self) -> None:
        try:

            sma_below = self.context.indicator_value(self._id_sma_below)
            sma_above = self.context.indicator_value(self._id_sma_above)

        except UnavailableData as e:
            logger.warning(e)
            self.on_wait()

        else :

            if not detect_convergence(sma_below,sma_above):
                self.on_fail()
            else:
                self.on_success()

    def on_success(self) -> None:
        self.context.transition_to(self.next)

    def on_fail(self) -> None:
        self.context.first_step()

    def on_wait(self) -> None:
        self.context.transition_to(self)
