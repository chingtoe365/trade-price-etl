from enum import Enum


class Metrics(Enum):
    DOUBLE_PEG = 'double_peg'
    # Go up more than 1% in 1 minute
    # TODO: better documentation elsewhere
    VOLATILE_UP_1_1 = 'volatile_up_1_1'
    # Go up more than 1% in 5 minutes
    VOLATILE_UP_1_5 = 'volatile_up_1_5'
    # Go down more than 1% in 1 minute
    VOLATILE_DOWN_1_1 = 'volatile_down_1_1'
    # Go down more than 1% in 5 minutes
    VOLATILE_DOWN_1_5 = 'volatile_down_1_5'

    def __str__(self):
        return self.value


class MetricsShortDescription(Enum):
    DOUBLE_PEG = 'Swinging between two points for a while'
    VOLATILE_UP_1_1 = 'Go up more than 1% in 1 minute'
    VOLATILE_UP_1_5 = 'Go up more than 1% in 5 minutes'
    VOLATILE_DOWN_1_1 = 'Go down more than 1% in 1 minute'
    VOLATILE_DOWN_1_5 = 'Go down more than 1% in 5 minutes'

    def __str__(self):
        return self.value
