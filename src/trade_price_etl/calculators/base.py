from abc import abstractmethod


class CalculatorBase:

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def compute(cls, price_item, df):
        raise NotImplementedError
