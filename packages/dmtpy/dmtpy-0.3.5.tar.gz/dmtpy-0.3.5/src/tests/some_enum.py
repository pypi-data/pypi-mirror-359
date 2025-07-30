"""Some Enum"""
from enum import Enum
from enum import auto


class SomeEnum(Enum):
    """Some Enum"""
    OPTION1 = auto()
    OPTION2 = auto()


    def label(self):
        """Get the label"""
        if self == SomeEnum.OPTION1:
            return "Option number 1"
        if self == SomeEnum.OPTION2:
            return "Option number 2"
