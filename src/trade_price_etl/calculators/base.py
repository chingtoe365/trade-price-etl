from abc import abstractmethod


class CalculatorBase:

    def __init__(self):
        pass

    @abstractmethod
    @classmethod
    def compute(cls, price_item, df):
        raise NotImplementedError
