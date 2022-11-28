from abc import abstractmethod


class CalculatorBase:
    def __init__(self):
        pass

    @abstractmethod
    def compute(self):
        raise NotImplementedError
