from abc import abstractmethod

from trade_price_etl.storage.real_time_metric import RTMS


class CalculatorBase:
    _compute_frequency = 0.5

    def __init__(self):
        pass

    @abstractmethod
    def compute(self):
        raise NotImplementedError
