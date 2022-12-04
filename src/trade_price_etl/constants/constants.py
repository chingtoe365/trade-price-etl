from enum import Enum


class Metrics(Enum):
    DOUBLE_PEG = 'double_peg'

    def __str__(self):
        return self.value
