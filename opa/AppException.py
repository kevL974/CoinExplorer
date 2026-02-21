class AppError(Exception):
    pass

class UnavailableData(AppError):
    pass

class UnavailablePriceData(UnavailableData):
    pass

class UnavailableIndicatorData(UnavailableData):
    pass

class StepError(AppError):
    """Error linked to a step of the strategy used by the bot."""

